#[starknet::contract]
mod contract {
    use starknet::ContractAddress;
    use starknet::get_caller_address;

    // Storage types & traits
    use starknet::storage::{Map, StorageMapReadAccess, StorageMapWriteAccess};
    use starknet::storage_access::Store;

    #[storage]
    struct Storage {
        owner: ContractAddress,
        balances: Map<ContractAddress, u256>,
        total_supply: u256,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        Transfer: TransferEvent,
    }

    #[derive(Drop, starknet::Event)]
    struct TransferEvent {
        from: ContractAddress,
        to: ContractAddress,
        value: u256,
    }

    // Constructor stays as a regular entrypoint (uses ContractState, not Storage)
    #[constructor]
    fn constructor(ref self: ContractState, initial_supply: u256) {
        let owner = get_caller_address();
        self.owner.write(owner);
        self.balances.write(owner, initial_supply);
        self.total_supply.write(initial_supply);
    }

    // Public interface
    #[starknet::interface]
    trait IToken<TContractState> {
        fn transfer(ref self: TContractState, to: ContractAddress, value: u256);
        fn balance_of(self: @TContractState, account: ContractAddress) -> u256;
        fn total_supply(self: @TContractState) -> u256;
        fn owner(self: @TContractState) -> ContractAddress;
    }

    // Embed the ABI: functions below are exported without needing #[external]
    #[abi(embed_v0)]
    impl TokenImpl of IToken<ContractState> {
        fn transfer(ref self: ContractState, to: ContractAddress, value: u256) {
            let caller = get_caller_address();

            let from_balance = self.balances.read(caller);
            assert(from_balance >= value, 'Insufficient balance');

            let to_balance = self.balances.read(to);
            self.balances.write(caller, from_balance - value);
            self.balances.write(to, to_balance + value);

            self.emit(Event::Transfer(TransferEvent { from: caller, to, value }));
        }

        fn balance_of(self: @ContractState, account: ContractAddress) -> u256 {
            self.balances.read(account)
        }

        fn total_supply(self: @ContractState) -> u256 {
            self.total_supply.read()
        }

        fn owner(self: @ContractState) -> ContractAddress {
            self.owner.read()
        }
    }
}
