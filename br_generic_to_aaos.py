#!/usr/bin/env python3
import argparse
import json
import os
import sys
import libs.adb.device as adb
import libs.vhal_emulator.vhal_emulator as vhal_emu
from libs.vhal_emulator.vhal_prop_consts_2_0 import vhal_props, vhal_vehicle_area, vhal_types
from libs.remotive.subscribe import subscribe, get_proper_signal_value
from inspect import getmembers


class BrokerToAAOS:
    def __init__(self, adb_dev):
        # Get the emulator device via adb only once
        self.adb_dev = adb_dev
        self.vhal = vhal_emu.Vhal()
        self.signals_map = {}  # Map of signal names to property IDs and types
        self.signals_to_subscribe = []  # List of (namespace, signal) tuples to subscribe to
        
    def add_signal_mapping(self, signal_name, property_id, area_id=vhal_vehicle_area.GLOBAL, value_type=None, namespace=None):
        """Add a mapping from signal name to VHAL property ID"""
        if value_type is None:
            value_type = self.determine_value_type(property_id)
            
        self.signals_map[signal_name] = {
            'property_id': property_id,
            'area_id': area_id,
            'value_type': value_type,
            'namespace': namespace
        }
        
        # Add the property to VHAL's property map
        self.vhal._propToType[property_id] = value_type
        
        # If namespace is provided, add this signal to the subscription list
        if namespace:
            if (namespace, signal_name) not in self.signals_to_subscribe:
                self.signals_to_subscribe.append((namespace, signal_name))
                print(f"Added subscription: {namespace}/{signal_name}")
        
        print(f"Added mapping: {signal_name} -> Property ID: 0x{property_id:08x}, Type: 0x{value_type:08x}")
    
    def determine_value_type(self, property_id):
        """Try to determine the value type from the property ID"""
        type_mask = property_id & vhal_types.TYPE_MASK
        
        if type_mask == vhal_types.TYPE_STRING:
            return vhal_types.TYPE_STRING
        elif type_mask == vhal_types.TYPE_BOOLEAN:
            return vhal_types.TYPE_BOOLEAN
        elif type_mask == vhal_types.TYPE_INT32 or type_mask == vhal_types.TYPE_INT32_VEC:
            return vhal_types.TYPE_INT32
        elif type_mask == vhal_types.TYPE_INT64 or type_mask == vhal_types.TYPE_INT64_VEC:
            return vhal_types.TYPE_INT64
        elif type_mask == vhal_types.TYPE_FLOAT or type_mask == vhal_types.TYPE_FLOAT_VEC:
            return vhal_types.TYPE_FLOAT
        elif type_mask == vhal_types.TYPE_BYTES:
            return vhal_types.TYPE_BYTES
        elif type_mask == vhal_types.TYPE_MIXED:
            return vhal_types.TYPE_MIXED
        else:
            # Default to INT32 if we can't determine
            return vhal_types.TYPE_INT32
    
    def convert_value(self, value, value_type):
        """Convert the value to the appropriate type"""
        if value_type in (vhal_types.TYPE_INT32, vhal_types.TYPE_INT32_VEC):
            return int(value)
        elif value_type in (vhal_types.TYPE_INT64, vhal_types.TYPE_INT64_VEC):
            return int(value)
        elif value_type in (vhal_types.TYPE_FLOAT, vhal_types.TYPE_FLOAT_VEC):
            return float(value)
        elif value_type in (vhal_types.TYPE_BOOLEAN,):
            return value.lower() in ('true', 'yes', '1', 'on') if isinstance(value, str) else bool(value)
        else:
            # For string and bytes, return as is
            return value
    
    def redirect_signals_to_aaos(self, signals):
        """Process incoming signals from the broker and forward them to AAOS"""
        for signal in signals:
            signal_val = get_proper_signal_value(signal)
            signal_name = signal.id.name
            
            print(f"{signal_name} {signal.id.namespace.name} {signal_val}")
            
            # Check if we have a mapping for this signal
            if signal_name in self.signals_map:
                mapping = self.signals_map[signal_name]
                property_id = mapping['property_id']
                area_id = mapping['area_id']
                value_type = mapping['value_type']
                
                # Convert the value to the appropriate type
                converted_value = self.convert_value(signal_val, value_type)
                
                print(f"Forwarding signal to AAOS as property ID: 0x{property_id:08x}, value: {converted_value}")
                
                # Set the property in AAOS
                try:
                    self.vhal.set_property(property_id, area_id, converted_value)
                    reply = self.vhal.rx_msg()
                    print(f"Response from AAOS: {reply}")
                except Exception as e:
                    print(f"Error setting property: {e}")
            else:
                print(f"No mapping found for signal: {signal_name}")
    
    def load_mappings_from_json(self, json_file):
        """Load signal mappings from a JSON file (only array of objects format is supported)"""
        try:
            with open(json_file, 'r') as f:
                mapping_data = json.load(f)
            
            # Verify it's an array
            if not isinstance(mapping_data, list):
                print(f"Error: JSON mapping file must be an array of objects. Found {type(mapping_data).__name__} instead.")
                return False
            
            # Process each mapping object in the array
            for mapping in mapping_data:
                self._add_mapping_from_json_obj(mapping)
            
            print(f"Successfully loaded mappings from {json_file}")
            return True
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from {json_file}: {e}")
            return False
        except Exception as e:
            print(f"Error loading mappings from {json_file}: {e}")
            return False
    
    def _add_mapping_from_json_obj(self, mapping):
        """Add a mapping from a JSON object"""
        # Check required fields
        if 'signal' not in mapping:
            print(f"Warning: Skipping mapping with missing 'signal' field: {mapping}")
            return
        
        if 'propertyId' not in mapping:
            print(f"Warning: Skipping mapping with missing 'propertyId' field: {mapping}")
            return
        
        if 'namespace' not in mapping:
            print(f"Warning: Skipping mapping with missing 'namespace' field: {mapping}")
            return
        
        signal_name = mapping['signal']
        namespace = mapping['namespace']
        
        # Convert property ID from various formats
        if isinstance(mapping['propertyId'], str):
            # Handle hex strings (0x...) or decimal strings
            property_id = int(mapping['propertyId'], 0)
        else:
            # Handle direct integer values
            property_id = int(mapping['propertyId'])
        
        # Get area ID if specified
        area_id = vhal_vehicle_area.GLOBAL
        if 'areaId' in mapping:
            if isinstance(mapping['areaId'], str):
                area_id = int(mapping['areaId'], 0)
            else:
                area_id = int(mapping['areaId'])
        
        # Get value type if specified
        value_type = None
        if 'valueType' in mapping:
            # Check if this is a string name of a type constant
            if isinstance(mapping['valueType'], str):
                if mapping['valueType'].upper() in ['STRING', 'TYPE_STRING']:
                    value_type = vhal_types.TYPE_STRING
                elif mapping['valueType'].upper() in ['BOOLEAN', 'TYPE_BOOLEAN']:
                    value_type = vhal_types.TYPE_BOOLEAN
                elif mapping['valueType'].upper() in ['INT32', 'TYPE_INT32']:
                    value_type = vhal_types.TYPE_INT32
                elif mapping['valueType'].upper() in ['INT64', 'TYPE_INT64']:
                    value_type = vhal_types.TYPE_INT64
                elif mapping['valueType'].upper() in ['FLOAT', 'TYPE_FLOAT']:
                    value_type = vhal_types.TYPE_FLOAT
                elif mapping['valueType'].upper() in ['BYTES', 'TYPE_BYTES']:
                    value_type = vhal_types.TYPE_BYTES
                elif mapping['valueType'].upper() in ['MIXED', 'TYPE_MIXED']:
                    value_type = vhal_types.TYPE_MIXED
                else:
                    # Try to parse as a hex or decimal value
                    try:
                        value_type = int(mapping['valueType'], 0)
                    except ValueError:
                        print(f"Warning: Unknown value type '{mapping['valueType']}' for signal {signal_name}")
            else:
                # Assume it's a numeric value
                value_type = int(mapping['valueType'])
        
        # Add the mapping
        self.add_signal_mapping(signal_name, property_id, area_id, value_type, namespace)
    
    def forward_signals(self, broker_url, api_key):
        """Start forwarding signals from broker to AAOS"""
        try:
            # Check if we have any signals specified in the mapping file
            if not self.signals_to_subscribe:
                print("Error: No signals to subscribe to. Your JSON mapping file must include the 'namespace' field for each signal.")
                sys.exit(1)
            
            # Set default values if not provided
            if broker_url is None:
                broker_url = "http://127.0.0.1:50051"
            if api_key is None:
                api_key = "offline"
                
            # Subscribe to signals and start forwarding
            print(f"Subscribing to signals: {self.signals_to_subscribe}")
            print(f"Connecting to broker at {broker_url}")
            subscribe(broker_url, api_key, self.signals_to_subscribe, 
                     on_subscribe=self.redirect_signals_to_aaos, 
                     on_change=False)
                
        except Exception as e:
            print(f"Error starting signal forwarding: {e}")
            sys.exit(1)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Forward signals from broker to Android Automotive OS via VHAL')
    parser.add_argument('--mappings-file', type=str, required=True, help='JSON file containing signal to property mappings (array of objects format)')
    parser.add_argument('--broker-url', type=str, help='URL of the RemotiveBroker (default: http://127.0.0.1:50051)')
    parser.add_argument('--api-key', type=str, help='API key for broker access (default: "offline")')
    
    return parser.parse_args()


def main():
    # Parse arguments
    args = parse_arguments()
    
    # Check for required mappings file
    if not os.path.exists(args.mappings_file):
        print(f"Error: Mappings file not found: {args.mappings_file}")
        sys.exit(1)
    
    # Get emulator device
    try:
        adb_device = adb.get_emulator_device()
        print(f"Connected to emulator device")
    except Exception as e:
        print(f"Error connecting to emulator: {e}")
        return
    
    # Create broker to AAOS bridge
    broker_aaos = BrokerToAAOS(adb_device)
    
    # Load mappings from JSON file
    if not broker_aaos.load_mappings_from_json(args.mappings_file):
        print(f"Error loading mappings from file. Exiting.")
        sys.exit(1)
    
    # Start forwarding signals
    broker_aaos.forward_signals(args.broker_url, args.api_key)


if __name__ == "__main__":
    main() 