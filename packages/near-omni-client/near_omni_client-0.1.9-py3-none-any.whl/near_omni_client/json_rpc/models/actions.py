from py_near_primitives.py_near_primitives import (
    AddKeyAction,
    CreateAccountAction,
    DelegateAction,
    DeleteAccountAction,
    DeleteKeyAction,
    DeployContractAction,
    FunctionCallAction,
    SignedDelegateAction,
    StakeAction,
    TransferAction,
)

Action = (
    DelegateAction
    | TransferAction
    | DeleteAccountAction
    | FunctionCallAction
    | DeployContractAction
    | CreateAccountAction
    | SignedDelegateAction
    | DeleteKeyAction
    | AddKeyAction
    | StakeAction
)
