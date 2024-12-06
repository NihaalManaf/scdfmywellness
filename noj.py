noj = {
    "conversations" : {
        "/start" : ['genesis'],
        "/register" : ['awaiting_code', 'code_auth']
    }, 

    "states" : {
        "genesis" : {   
            "return msg" : "/start message goes here",
            'info_payload_update' : {},
            'handling_fn' : 'genesis',
        },
        "awaiting_code" : {
            "return msg" : "Please enter the verification code",
            'info_payload_update' : {
                "awaiting_code" : "user_input"
            },
            'handling_fn' : 'send_text',
        },
        "code_auth" : {
            "return msg" : "Code authenticated",
            'info_payload_update' : {},
            'handling_fn' : 'send_text',
        }
    
    }
}

# all states must be found in in a conversation. A state can be in multiple conversations but a conversation must have at least one state.

