# Generated protobuf files
# This file makes the proto directory a Python package

try:
    from . import service_pb2
    from . import service_pb2_grpc
except ImportError as e:
    print(f"Warning: Could not import protobuf modules: {e}")
    print("You may need to regenerate the protobuf files.")
