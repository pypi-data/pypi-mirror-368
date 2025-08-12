import random
from opentelemetry import trace
from opentelemetry.sdk.trace.id_generator import RandomIdGenerator
from ..types.session_type import SessionType
from ..constants import MULTIPLAYER_TRACE_DEBUG_PREFIX, MULTIPLAYER_TRACE_CONTINUOUS_DEBUG_PREFIX

class SessionRecorderRandomIdGenerator(RandomIdGenerator):
    def __init__(self):
        super().__init__()
        self.session_type = ''
        self.session_short_id = ''
    
    def set_session_id(self, session_short_id: str, session_type: SessionType) -> None:
        self.session_short_id = session_short_id
        self.session_type = session_type

    def generate_span_id(self) -> int:
        span_id = random.getrandbits(64)
        while span_id == trace.INVALID_SPAN_ID:
            span_id = random.getrandbits(64)
        return span_id

    def generate_trace_id(self) -> int:
        trace_id = random.getrandbits(128)
        while trace_id == trace.INVALID_TRACE_ID:
            trace_id = random.getrandbits(128)

        if self.session_short_id:
            session_type_prefix = ""

            if self.session_type == SessionType.CONTINUOUS:
                session_type_prefix = MULTIPLAYER_TRACE_CONTINUOUS_DEBUG_PREFIX
            else:
                session_type_prefix = MULTIPLAYER_TRACE_DEBUG_PREFIX

            # Create a prefix by combining the session type prefix and session short ID
            prefix = f"{session_type_prefix}{self.session_short_id}"
            
            # Convert the hex prefix to an integer
            prefix_int = int(prefix, 16)
            
            # Create a trace ID by combining the prefix with random bits
            # We'll use the prefix for the high-order bits and random bits for the rest
            random_bits = random.getrandbits(128 - len(prefix) * 4)  # 4 bits per hex character
            combined_trace_id = (prefix_int << (128 - len(prefix) * 4)) | random_bits

            return combined_trace_id

        return trace_id
