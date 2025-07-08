// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "./ISuperPromptAuction.sol";

contract SuperPromptAuction is ISuperPromptAuction {
    address public owner;
    uint256 public auctionEnd;
    bool public started;
    bool public ended;

    address public highestBidder;
    uint256 public highestBid;
    string public winningPrompt;

    event AuctionStarted(uint256 endTime);
    event NewBid(address indexed bidder, uint256 amount, string promptText);
    event AuctionEnded(address indexed winner, uint256 amount, string promptText);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    function startAuction(uint256 duration) external override onlyOwner {
        require(!started || ended, "Auction already in progress");
        started = true;
        ended = false;
        auctionEnd = block.timestamp + duration;
        highestBid = 0;
        highestBidder = address(0);
        winningPrompt = "";
        emit AuctionStarted(auctionEnd);
    }

    function bid(string calldata promptText) external payable override {
        require(started && block.timestamp < auctionEnd, "Auction not active");
        require(msg.value > highestBid, "Bid too low");
        highestBid = msg.value;
        highestBidder = msg.sender;
        winningPrompt = promptText;
        emit NewBid(msg.sender, msg.value, promptText);
    }

    function endAuction() external override {
        require(started, "Auction not started");
        require(block.timestamp >= auctionEnd, "Auction not yet ended");
        require(!ended, "Auction already ended");
        ended = true;
        emit AuctionEnded(highestBidder, highestBid, winningPrompt);
    }

    function getWinner() external view override returns (address) {
        require(ended, "Auction not ended");
        return highestBidder;
    }

    function getWinningPrompt() external view override returns (string memory) {
        require(ended, "Auction not ended");
        return winningPrompt;
    }

    function withdraw() external override onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}
