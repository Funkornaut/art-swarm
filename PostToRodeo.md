# Steps

1. **Clone collection contract from factory [ONE TIME]**
    - Call `createMultiTokenCollection` on factory contract here: https://basescan.org/address/0xf1814213A5Ef856aAa1fdb0F7f375569168d8E73#writeProxyContract
    - Use any number as `contractCreationNonce`. This is used to prevent duplicate calls from the same caller at the same time.
    - Pass in a metadata URI for `contractURI`.
        - This metadata isn’t used internally on Rodeo, but is used by other web3 marketplaces like OpenSea to render the collection. See specification here: https://docs.opensea.io/docs/contract-level-metadata
        - You can use this one as a default: https://bafybeieu72fdhr5caaop5uwwlnc6p6pfsotb6rolovk7mhc6k62q4c7nnq.ipfs.dweb.link/metadata.json to set the collection’s name as “Rodeo posts”.
2. **Add Rodeo drop market as a minter [ONE TIME]**
    - Find the newly created collection from the “Logs” tab in the transaction from above.
    - Call `grantMinter` on newly created collection with this address as the argument: `0x132363a3bbf47E06CF642dd18E9173E364546C99`.
3. **Create token on newly created collection**
    - Call `createToken` on the new collection contract.
    - Pass in any integer for `tokenId`.
        - This is used to differentiate between tokens, and are globally unique for a given collection.
        - We recommend you increment by one to avoid errors.
        - *[COMING] We can provide an API endpoint to get the next token ID.*
    - Pass in token metadata for `tokenURI`.
        - Rodeo’s backend currently only supports IPFS links in the format `ipfs://<CID>` with image and video asset types.
        - If helpful, https://rodeo.club expects this TypeScript typing
            
            ```tsx
            export *type* TokenMetadata = {
               category: *string* | *undefined*;
               description: *string* | *undefined*;
               image: *string*;
               name: *string*;
            };
            ```
            
        - `image` value is expected to be of format `ipfs://<CID>`
    - Pass in a unix timestamp in seconds for `mintEndTime`.
        - Rodeo posts generally last for 24 hours, and we recommend passing in 24 hours from post time as the end time to ensure the post behaves properly on https://rodeo.club.
        - Posts with durations <23 hours and above 25 hours are filtered out on discovery surfaces (explore, feed) on the app, but are still available on profiles and directly on post pages.

4. **Create sale on drop market**
    - Call `createFixedPriceSale` on drop market contract: `0x132363a3bbf47E06CF642dd18E9173E364546C99`.
    - Pass in your contract address for `multiTokenContract`.
    - Pass in the token ID you used in (3) above for `tokenId`.
    - Pass in 0 for `pricePerQuantity`. The mint fee is applied on top of this price. Sale terms above 0 are filtered out on the app at the moment.
    - Pass in where you want to get paid for `creatorPaymentAddress`.
    - Pass in 0 for `generalAvailabilityStartTime` to start the sale now.

If you’ve followed these steps, your posts should show up on Rodeo and is ready to be collected! Find us at the [Help Center](https://help.rodeo.club/hc/en-us) if you run into any issues.

# Resources

## Base Sepolia testnet deployments

- Collection factory: `0x0D0c39Ad9f93ea8e775Eaa1d2Fd410f5534dFaFE`
- Drop market: `0xE750E597bFcDbe1C27322e729f1796B52DFCddDb`