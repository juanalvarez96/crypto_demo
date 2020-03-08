# -*- coding: utf-8 -*-
# ==================================================
# ==================== META DATA ===================
# ==================================================
__author__ = "Daxeel Soni"
__url__ = "https://daxeel.github.io"
__email__ = "daxeelsoni44@gmail.com"
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daxeel Soni"

# ==================================================
# ================= IMPORT MODULES =================
# ==================================================
import hashlib
import datetime
import json
from colorama import Fore, Back, Style
import time
import sys
import functools
import pdb

USER_COINS = 10

# ==================================================
# =============== TRANSACTION CLASS ================
# ==================================================

class Transaction:
    """
        Create a transaction
    """
    def __init__(self, amount, sender, receiver):
        self.amount = amount
        self.sender = sender.identity
        self.receiver = receiver.identity
        self.timestamp = str(datetime.datetime.now())

    def __str__(self):
        transaction = "%s transferred %d to %s.\n" % (self.sender, self.amount, self.receiver)
        return transaction

# ==================================================
# =================== USER CLASS ===================
# ==================================================

class User:
    """
        Create a new user with NiceCoins
    """
    def __init__(self, identity, coins=USER_COINS):
        self.identity = identity
        self.wallet = coins

    def __str__(self):
        user = "%s currently has %s NiceCoins.\n" % (self.identity, str(self.wallet))
        return user

    def makePayment(self, amount):
        if amount <= self.wallet:
            self.wallet -= amount
        else:
            raise Exception("Transfer exceeds user's wallet!")
    
    def receiveTransfer(self, amount):
        self.wallet += amount

# ==================================================
# =================== BLOCK CLASS ==================
# ==================================================

class Block:
    """
        Create a new block in chain with metadata
    """
    def __init__(self, previousHash="", index=0):
        self.index = index
        self.previousHash = previousHash
        self.transactions = []
        self.timestamp = str(datetime.datetime.now())
        self.nonce = 0
        self.transactionLimit = 8
        if previousHash == "":
            self.hash = self.calculateGenesisHash("Genesis block")
        else:
            self.hash = ""

    def __str__(self):
        block = "Created at %s\n" % self.timestamp
        if self.hash != '' and self.hash != None:
            block += "Hash: %s.\n" % self.hash
        if self.previousHash == '':
            block += "This is the genesis block.\n"
        else:
            block += "Previous hash: %s.\n" % self.previousHash
        if len(self.transactions) > 0:
            block += "Transactions:\n"
            for t in self.transactions:
                block += "\t%s" % str(t)
        else:
            block += "The block has no transactions.\n"
        return block

    def calculateHash(self):
        """
            Method to calculate hash from transaction data
        """
        if len(self.transactions) < self.transactionLimit:
            raise Exception("Transaction list should be completed before adding the block to the chain.")

        hashTransactions = [
            hashlib.sha256(
                str(t.amount) +
                str(t.sender) +
                str(t.receiver) +
                str(t.timestamp) +
                str(self.nonce)).hexdigest()
            for t in self.transactions
        ]
        hash01 = hashlib.sha256(hashTransactions[0] + hashTransactions[1]).hexdigest()
        hash23 = hashlib.sha256(hashTransactions[2] + hashTransactions[3]).hexdigest()
        hash45 = hashlib.sha256(hashTransactions[4] + hashTransactions[5]).hexdigest()
        hash67 = hashlib.sha256(hashTransactions[6] + hashTransactions[7]).hexdigest()
        hash0123 = hashlib.sha256(hash01 + hash23).hexdigest()
        hash4567 = hashlib.sha256(hash45 + hash67).hexdigest()
        merkleRoot = hashlib.sha256(hash0123 + hash4567).hexdigest()
        return merkleRoot

    def calculateGenesisHash(self, data):
        """
            Method to calculate the genesis hash from metadata
        """
        hashData = str(self.index) + str(data) + self.timestamp + self.previousHash + str(self.nonce)
        return hashlib.sha256(hashData).hexdigest()

    def mineBlock(self, difficulty):
        """
            Method for Proof of Work
        """
        if self.previousHash != '':
            
            print Back.RED + "\n[Status] Mining block (" + str(self.index) + ") with PoW ..."
            startTime = time.time()
            while self.hash[:difficulty] != "0"*difficulty:
                self.nonce += 1
                self.hash = self.calculateHash()

            endTime = time.time()
            print Back.BLUE + "[ Info ] Time Elapsed : " + str(endTime - startTime) + " seconds."
            print Back.BLUE + "[ Info ] Mined Hash : " + self.hash
            print Style.RESET_ALL

# ==================================================
# ================ BLOCKCHAIN CLASS ================
# ==================================================
class Blockchain:
    """
        Initialize blockchain
    """
    def __init__(self, difficulty=3):
        self.chain = [self.createGenesisBlock()]
        self.difficulty = difficulty
        self.addBlock()

    def __str__(self):
        current = self.chain[-1]
        chain = "Blockchain for NiceCoins!\n\n"
        chain += "Current block:\n"
        chain += str(current)
        try:
            previous = self.chain[-2]
            chain += "\nPrevious block:\n"
            chain += str(previous)
        except Exception:
            pass
        return chain

    def createGenesisBlock(self):
        """
            Method create genesis block
        """
        return Block()

    def addBlock(self):
        """
            Method to add new block from Block class
        """
        previousBlock = self.chain[-1]
        try:
            previousBlock.mineBlock(self.difficulty)
            newBlock = Block(
                previousHash=previousBlock.hash,
                index=len(self.chain)
            )
            self.chain.append(newBlock)
            self.writeBlocks()
        except Exception as err:
            print("The block is not ready: \n" + str(err))

    def addTransaction(self, amount, sender, receiver):
        """
            Add a transaction to the current block
        """
        legitTransaction = self.checkDoubleSpending(amount, sender, receiver)
        if legitTransaction == True:
            raise Exception("Cannot complete transaction: ⁄nDouble spending detected.")
        block = self.chain[-1]
        if len(block.transactions) < block.transactionLimit:
            try:
                sender.makePayment(amount)
                block.transactions.append(Transaction(
                    amount,
                    sender,
                    receiver))
                receiver.receiveTransfer(amount)
            except Exception as err:
                print("Cannot complete transaction: \n", str(err))
        else:
            raise Exception("Transaction list is full: add block to chain!")

    def writeBlocks(self):
        """
            Method to write new mined block to blockchain
        """
        dataFile = file("chain.txt", "w")
        chainData = []
        for eachBlock in self.chain:
            chainData.append(eachBlock.__dict__)
        dataFile.write(json.dumps(chainData, indent=4))
        dataFile.close()
    
    def checkDoubleSpending(self, amount, sender, receiver):
        """
            This method will check all the transactions from the past of the sender.
        """
        history = []
        #pdb.set_trace()
        for block in self.chain:
            for transaction in block.transactions:
                if str(transaction.sender) == str(sender.identity) :
                    history.append(-1 * int(transaction.amount))    
                if str(transaction.receiver) == str(sender.identity) :
                    history.append(1 * int(transaction.amount))
        if len(history)==0:
            return False
        else:
            availableSaldo = functools.reduce(lambda x,y: x+y, history) + USER_COINS
            if availableSaldo < amount:
                return True
            else:
                return False


# ==================================================
# ================== SIMPLE TESTS ==================
# ==================================================

# Run these commands in console to test the blockchain interactively:
"""
from chain import *
"""

# Users are initiated with 10 NiceCoins:
"""
j = User('Juan')
v = User('Victoria')
"""

# Create the blockchain
"""
c = Blockchain()
print(c)
c.addTransaction(4, j, v)
c.addTransaction(10, v, j)
"""

# Status: Victoria: 2 and Juan: 18
"""
print(j)
print(v)
"""

# Transaction not possible because of Victoria's balance:
"""
c.addTransaction(5, v, j)
"""

# Possible transactions:
"""
c.addTransaction(2, v, j)
c.addTransaction(10, j, v)
c.addTransaction(2, v, j)
c.addTransaction(2, v, j)
c.addTransaction(2, v, j)
"""

# Block full, cannot add more transactions:
"""
c.addTransaction(6, j, v)
"""

# Add the block to the blockchain
"""
c.addBlock()
"""

# Transaction is now possible:
"""
c.addTransaction(6, j, v)
print(c)
"""

# To do the double-spending prevention:
"""
https://www.investopedia.com/ask/answers/061915/how-does-block-chain-prevent-doublespending-bitcoins.asp
"""
