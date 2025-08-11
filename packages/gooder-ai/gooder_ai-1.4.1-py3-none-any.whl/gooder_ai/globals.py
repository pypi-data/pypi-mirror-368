from gooder_ai.types import AmplifyEnv

# The following configuration values are environment-specific and need to be updated when switching to a new environment.
# For example, we are currently on environment "seventeen," and when transitioning to environment "eighteen,"
# these values should be updated accordingly.
Amplify_Env: dict[str, AmplifyEnv] = {
    "twenty": {
        "API_URL": "https://kuzk6av7qzerlbf3ydh4attvjm.appsync-api.us-east-1.amazonaws.com/graphql",  # GraphQL API URL
        "App_Client_ID": "6fd62mcj6gm6284lsh8s5lqtq3",  # App_Client_ID is the client ID for an app in a Cognito User Pool
        "Identity_Pool_ID": "us-east-1:f6644ce2-5684-4bfa-b1b7-7fcab596db16",  # Identity_Pool_ID is the ID for an Amazon Cognito Identity Pool
        "User_Pool_ID": "us-east-1_hIY8Hv3Tq",  # UserPool_ID is the ID for the Cognito User Pool that manages user authentication
        "Bucket_Name": "mlviz1049e7ed428840c3bb9773b134209edd0293f-twenty",  # S3 bucket name storing datasets and configs
        "Validation_API_URL": "https://3l5mgwry0m.execute-api.us-east-1.amazonaws.com/twenty",  # Validation API URL
        "Base_URL": "https://latest2.gooder.ai",  # This is the URL for gooder ai application
        "AWS_Region_Name": "us-east-1",
    },
    "nineteen": {
        "API_URL": "https://qnlnkyjmsjfmfclaw4c57sh3sm.appsync-api.us-east-1.amazonaws.com/graphql",  # GraphQL API URL
        "App_Client_ID": "2683vvaemodl7tc9palj01mgsj",  # App_Client_ID is the client ID for an app in a Cognito User Pool
        "Identity_Pool_ID": "us-east-1:c8269f75-6579-4f78-9835-d10ce0d5af7b",  # Identity_Pool_ID is the ID for an Amazon Cognito Identity Pool
        "User_Pool_ID": "us-east-1_k0t79dhVU",  # UserPool_ID is the ID for the Cognito User Pool that manages user authentication
        "Bucket_Name": "mlviz1049e7ed428840c3bb9773b134209eddb6e11-nineteen",  # S3 bucket name storing datasets and configs
        "Validation_API_URL": "https://unqoyoggm4.execute-api.us-east-1.amazonaws.com/nineteen/validate",  # Validation API URL
        "Base_URL": "https://app2.gooder.ai",  # This is the URL for gooder ai application
        "AWS_Region_Name": "us-east-1",
    },
    "eighteen": {
        "API_URL": "https://y5u2lvnrl5flblw45ojgyckxau.appsync-api.us-east-1.amazonaws.com/graphql",  # GraphQL API URL
        "App_Client_ID": "5ml0oe8lbn6e9ail331gmg11n9",  # App_Client_ID is the client ID for an app in a Cognito User Pool
        "Identity_Pool_ID": "us-east-1:60a5f15a-7736-4d81-9f7c-c2306deed47f",  # Identity_Pool_ID is the ID for an Amazon Cognito Identity Pool
        "User_Pool_ID": "us-east-1_M38tSlB29",  # UserPool_ID is the ID for the Cognito User Pool that manages user authentication
        "Bucket_Name": "mlviz1049e7ed428840c3bb9773b134209eddb4289-eighteen",  # S3 bucket name storing datasets and configs
        "Validation_API_URL": "https://l3tgixzm39.execute-api.us-east-1.amazonaws.com/eighteen/validate",  # Validation API URL
        "Base_URL": "https://v18.gooder.ai",  # This is the URL for gooder ai application
        "AWS_Region_Name": "us-east-1",
    },
    "seventeen": {
        "API_URL": "https://ojykj5ys3rflbprrjwiyi524oy.appsync-api.us-east-1.amazonaws.com/graphql",  # GraphQL API URL
        "App_Client_ID": "6hmbs2hm1dbpantdbpfnokina",  # App_Client_ID is the client ID for an app in a Cognito User Pool
        "Identity_Pool_ID": "us-east-1:9682a196-3376-4d36-b5d8-d46862f47d7b",  # Identity_Pool_ID is the ID for an Amazon Cognito Identity Pool
        "User_Pool_ID": "us-east-1_wzrj8LRkh",  # UserPool_ID is the ID for the Cognito User Pool that manages user authentication
        "Bucket_Name": "mlviz1049e7ed428840c3bb9773b134209edd111800-seventeen",  # S3 bucket name storing datasets and configs
        "Validation_API_URL": "https://htknl8tmxi.execute-api.us-east-1.amazonaws.com/seventeen/validate",  # Validation API URL
        "Base_URL": "https://v15.gooder.ai",  # This is the URL for gooder ai application
        "AWS_Region_Name": "us-east-1",
    },
    "staging": {
        "API_URL": "https://rn6bkti6hzaezpfyzgzbvaa3fa.appsync-api.us-east-1.amazonaws.com/graphql",  # GraphQL API URL
        "App_Client_ID": "6bbd33bs8sbfk5cnpe0pfsfs5j",  # App_Client_ID is the client ID for an app in a Cognito User Pool
        "Identity_Pool_ID": "us-east-1:b67ada79-b7a3-4f38-8313-0b5f6ef470b0",  # Identity_Pool_ID is the ID for an Amazon Cognito Identity Pool
        "User_Pool_ID": "us-east-1_GE4Ui0x7R",  # UserPool_ID is the ID for the Cognito User Pool that manages user authentication
        "Bucket_Name": "mlviz1049e7ed428840c3bb9773b134209edd824be-staging",  # S3 bucket name storing datasets and configs
        "Validation_API_URL": "https://gp2610lxad.execute-api.us-east-1.amazonaws.com/staging/validate",  # Validation API URL
        "Base_URL": "https://latest.gooder.ai",  # This is the URL for gooder ai application
        "AWS_Region_Name": "us-east-1",
    },
    "dev": {
        "API_URL": "https://6riyxyhr4rhadhiyy3nhowum6q.appsync-api.us-east-1.amazonaws.com/graphql",  # GraphQL API URL
        "App_Client_ID": "ahlo0e0ab16rjv7ra3bqjb863",  # App_Client_ID is the client ID for an app in a Cognito User Pool
        "Identity_Pool_ID": "us-east-1:e8c206d0-1657-4377-8454-b67d15f8211d",  # Identity_Pool_ID is the ID for an Amazon Cognito Identity Pool
        "User_Pool_ID": "us-east-1_PXgxYBLr4",  # UserPool_ID is the ID for the Cognito User Pool that manages user authentication
        "Bucket_Name": "mlviz1049e7ed428840c3bb9773b134209edd7ac58-dev",  # S3 bucket name storing datasets and configs
        "Validation_API_URL": "https://2vnjgkbgri.execute-api.us-east-1.amazonaws.com/dev/validate",  # Validation API URL
        "Base_URL": "https://dev.gooder.ai",  # This is the URL for gooder ai application
        "AWS_Region_Name": "us-east-1",
    },
    "last": {
        "API_URL": "https://xtuxhtrqjjbxfbxx2skked5jsq.appsync-api.us-east-1.amazonaws.com/graphql",  # GraphQL API URL
        "App_Client_ID": "4k1a9pcc4pcqv6ao427vdpreb",  # App_Client_ID is the client ID for an app in a Cognito User Pool
        "Identity_Pool_ID": "us-east-1:d1a00767-f728-46d5-8b52-f7cb5bfa95ef",  # Identity_Pool_ID is the ID for an Amazon Cognito Identity Pool
        "User_Pool_ID": "us-east-1_l0p9wx7ax",  # UserPool_ID is the ID for the Cognito User Pool that manages user authentication
        "Bucket_Name": "mlviz1049e7ed428840c3bb9773b134209edd3da0b-last",  # S3 bucket name storing datasets and configs
        "Validation_API_URL": "https://v42mzwajb8.execute-api.us-east-1.amazonaws.com/last/validate",  # Validation API URL
        "Base_URL": "https://last.gooder.ai",  # This is the URL for gooder ai application
        "AWS_Region_Name": "us-east-1",
    },
    "prod": {
        "API_URL": "https://kxoh7qajknfy5mbvkm4k44uip4.appsync-api.us-east-1.amazonaws.com/graphql",  # GraphQL API URL
        "App_Client_ID": "oghfnobrvhj6r732ifc00eobo",  # App_Client_ID is the client ID for an app in a Cognito User Pool
        "Identity_Pool_ID": "us-east-1:2404c01c-09b4-48a8-85be-ef1f249fe76a",  # Identity_Pool_ID is the ID for an Amazon Cognito Identity Pool
        "User_Pool_ID": "us-east-1_wbmSsrzn9",  # UserPool_ID is the ID for the Cognito User Pool that manages user authentication
        "Bucket_Name": "mlviz1049e7ed428840c3bb9773b134209edde85ba-prod",  # S3 bucket name storing datasets and configs
        "Validation_API_URL": "https://lq0jgkrn4d.execute-api.us-east-1.amazonaws.com/prod/validate",  # Validation API URL
        "Base_URL": "https://app.gooder.ai",  # This is the URL for gooder ai application
        "AWS_Region_Name": "us-east-1",
    },
}
