"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 27, 3, '', 'responses/invoke_procedure.proto')
_sym_db = _symbol_database.Default()
from ..responses import question_pb2 as responses_dot_question__pb2
from ..types import concept_value_pb2 as types_dot_concept__value__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n responses/invoke_procedure.proto\x12\x08protocol\x1a\x18responses/question.proto\x1a\x19types/concept_value.proto"Z\n\x17InvokeProcedureResponse\x12?\n\x0foutput_concepts\x18\x01 \x03(\x0b2\x16.protocol.ConceptValueR\x0eoutputConcepts"\xb0\x01\n\x19InvokeProcedureResponseV2\x12?\n\x08response\x18\x01 \x01(\x0b2!.protocol.InvokeProcedureResponseH\x00R\x08response\x128\n\x08question\x18\x02 \x01(\x0b2\x1a.protocol.QuestionResponseH\x00R\x08questionB\x18\n\x16response_discriminatorB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'responses.invoke_procedure_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_INVOKEPROCEDURERESPONSE']._serialized_start = 99
    _globals['_INVOKEPROCEDURERESPONSE']._serialized_end = 189
    _globals['_INVOKEPROCEDURERESPONSEV2']._serialized_start = 192
    _globals['_INVOKEPROCEDURERESPONSEV2']._serialized_end = 368