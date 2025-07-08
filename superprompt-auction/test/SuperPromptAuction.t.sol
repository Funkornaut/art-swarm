// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {SuperPromptAuction} from "../src/SuperPromptAuction.sol";

contract SuperPromptAuctionTest is Test {
    SuperPromptAuction public auction;
    address bidder1 = address(0x1);
    address bidder2 = address(0x2);

    function setUp() public {
        auction = new SuperPromptAuction();
    }

    function testStartAuction_setsEndTimeCorrectly() public {
        uint256 duration = 100;
        auction.startAuction(duration);
        assertEq(auction.auctionEnd(), block.timestamp + duration);
    }

    function testBid_acceptsValidHigherBidAndTracksPrompt() public {
        auction.startAuction(100);
        vm.deal(bidder1, 1 ether);
        vm.prank(bidder1);
        auction.bid{value: 1 ether}("hello");
        assertEq(auction.highestBid(), 1 ether);
        assertEq(auction.highestBidder(), bidder1);
        assertEq(auction.winningPrompt(), "hello");
    }

    function testBid_revertsIfLowerThanCurrent() public {
        auction.startAuction(100);
        vm.deal(bidder1, 1 ether);
        vm.prank(bidder1);
        auction.bid{value: 1 ether}("hi");

        vm.deal(bidder2, 0.5 ether);
        vm.prank(bidder2);
        vm.expectRevert("Bid too low");
        auction.bid{value: 0.5 ether}("low");
    }

    function testEndAuction_storesWinnerAndPrompt() public {
        auction.startAuction(100);
        vm.deal(bidder1, 1 ether);
        vm.prank(bidder1);
        auction.bid{value: 1 ether}("win");
        vm.warp(block.timestamp + 101);
        auction.endAuction();
        assertTrue(auction.ended());
        assertEq(auction.getWinner(), bidder1);
        assertEq(auction.getWinningPrompt(), "win");
    }

    function testGetWinner_returnsCorrectAddress() public {
        auction.startAuction(100);
        vm.deal(bidder1, 1 ether);
        vm.prank(bidder1);
        auction.bid{value: 1 ether}("yes");
        vm.warp(block.timestamp + 101);
        auction.endAuction();
        assertEq(auction.getWinner(), bidder1);
    }

    function testWithdraw_allowsOwnerToPullFunds() public {
        auction.startAuction(100);
        vm.deal(bidder1, 1 ether);
        vm.prank(bidder1);
        auction.bid{value: 1 ether}("pay");
        vm.warp(block.timestamp + 101);
        auction.endAuction();

        uint256 before = address(this).balance;
        auction.withdraw();
        assertEq(address(this).balance, before + 1 ether);
    }

    function testRevertWithdrawByNonOwner() public {
        auction.startAuction(100);
        vm.deal(bidder1, 1 ether);
        vm.prank(bidder1);
        auction.bid{value: 1 ether}("pay");
        vm.warp(block.timestamp + 101);
        auction.endAuction();

        vm.prank(bidder1);
        vm.expectRevert("Not owner");
        auction.withdraw();
    }
}
