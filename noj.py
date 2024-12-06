noj = {

    "conversations" : {
        "/start" : ['genesis'],
        "/register" : ['awaiting_code', 'code_auth']
    }, 

    "states" : {
        "genesis" : {   
            "return msg" : "/start message goes here",
            'info_payload_update' : {},
            'handling_fn' : 'send_text',
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


print(noj['states']['genesis']['return msg'])