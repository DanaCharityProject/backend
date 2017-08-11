This document lists the parts of the code in this branch we've added/edited after we branched off from master-


/tests

test_validators.py
    test_is_valid_phone_number() (40-54)
    
test_app.py
    test_put_community_resource_info() (236-348)




/app

api.py
    put_community_resource_edit()  (94-111))
    edited post method for community resource in api.py, was giving an error in testing without verified value(85)
    added import statements (6-7)

api.yml
    lines 196-243

models.py
    class CommunityResourceManager (148-172)
    added imports line 5
    added community resource exceptions (19-26)

validators.py
    added constants (9-11)
    is_valid_phone_number() (42-47)
    is_valid_community_resource_name() (49-54)


