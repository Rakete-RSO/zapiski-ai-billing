# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: user_verification.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'user_verification.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17user_verification.proto\x12\x10userverification\"\x1f\n\x0bUserRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"$\n\x12UserExistsResponse\x12\x0e\n\x06\x65xists\x18\x01 \x01(\x08\x32g\n\x10UserVerification\x12S\n\nVerifyUser\x12\x1d.userverification.UserRequest\x1a$.userverification.UserExistsResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_verification_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_USERREQUEST']._serialized_start=45
  _globals['_USERREQUEST']._serialized_end=76
  _globals['_USEREXISTSRESPONSE']._serialized_start=78
  _globals['_USEREXISTSRESPONSE']._serialized_end=114
  _globals['_USERVERIFICATION']._serialized_start=116
  _globals['_USERVERIFICATION']._serialized_end=219
# @@protoc_insertion_point(module_scope)
