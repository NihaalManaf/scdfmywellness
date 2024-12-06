noj = {
    "conversations" : ["/start", "/register", "/convomode"], #add routing conversation starter here

    "conversation_flows" : { #add conversation flow here by starting with the conversation starter and listing the states in the conversation
        "/start" : ['genesis'],
        "/register" : ['awaiting_code', 'code_auth'],
        "/convomode" : ['realtime_convomode']
    }, 

    "states" : { #add states here following the format below. The handling_fn name must be the name of the function in the library and preferabbly the state name
        "genesis" : {   
            "return msg" : "/start message goes here",
            'info_payload_update' : {},
            'handling_fn' : 'genesis',
        },
        "awaiting_code" : {
            "return msg" : "Please enter the verification code",
            'info_payload_update' : {},
            'handling_fn' : 'awaiting_code',
        },
        "code_auth" : {
            "return msg" : "Code authenticated",
            'info_payload_update' : {},
            'handling_fn' : 'code_auth',
        },
        "realtime_convomode" : {
            "return msg" : "null",
            'info_payload_update' : {},
            'handling_fn' : 'realtime_convomode',
        },
    
    }
}

# all states must be found in in a conversation. A state can be in multiple conversations but a conversation must have at least one state.

