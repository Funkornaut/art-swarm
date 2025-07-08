// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

interface ISuperPromptAuction {
    function startAuction(uint256 duration) external;
    function bid(string calldata promptText) external payable;
    function endAuction() external;
    function getWinner() external view returns (address);
    function getWinningPrompt() external view returns (string memory);
    function withdraw() external;
}
