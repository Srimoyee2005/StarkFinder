
mod contract {
    use starknet::ContractAddress;
    use starknet::get_caller_address;
    use starknet::storage_access::Storage;
    use starknet::emit;

    #[storage]
    struct Storage {
        owner: Storage::Value<ContractAddress>,
        balances: Storage::Map<ContractAddress, u256>,
        total_supply: Storage::Value<u256>,
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

    #[constructor]
    fn constructor(ref self: Storage, initial_supply: u256) {
        let owner = get_caller_address();
        self.owner.write(owner);
        self.balances.write(owner, initial_supply);
        self.total_supply.write(initial_supply);
    }

    #[external]
    fn transfer(ref self: Storage, to: ContractAddress, value: u256) {
        let caller = get_caller_address();
        let from_balance = self.balances.read(caller);
        assert(from_balance >= value, 'Insufficient balance');

        let to_balance = self.balances.read(to);
        self.balances.write(caller, from_balance - value);
        self.balances.write(to, to_balance + value);

        emit!(Event::Transfer(TransferEvent { from: caller, to, value }));
    }

    #[external]
    fn balance_of(self: @Storage, account: ContractAddress) -> u256 {
        self.balances.read(account)
    }

    #[external]
    fn total_supply(self: @Storage) -> u256 {
        self.total_supply.read()
    }

    #[external]
    fn owner(self: @Storage) -> ContractAddress {
        self.owner.read()
    }
}
