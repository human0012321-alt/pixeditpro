"""
PhonePe-Style Money Truncation App
A comprehensive financial truncation application with modern UI
Inspired by PhonePe's design language
"""

import decimal
from decimal import Decimal, ROUND_DOWN, ROUND_UP, ROUND_HALF_UP, ROUND_HALF_EVEN
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Union, Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
import csv
import hashlib
import logging
from collections import defaultdict, Counter
import random
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Color codes for terminal UI
class Colors:
    """ANSI color codes for terminal UI"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    WHITE = '\033[97m'
    MAGENTA = '\033[35m'
    ORANGE = '\033[33m'


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class UpiTransaction:
    """UPI-style transaction model"""
    transaction_id: str
    amount: Decimal
    truncated_amount: Decimal
    loss_amount: Decimal
    currency: str
    payer: str
    payee: str
    note: str
    status: str  # SUCCESS, FAILED, PENDING
    timestamp: datetime
    transaction_type: str  # SEND, RECEIVE, PAYMENT, REQUEST
    
    def to_dict(self):
        return {
            'id': self.transaction_id,
            'amount': float(self.amount),
            'truncated': float(self.truncated_amount),
            'loss': float(self.loss_amount),
            'currency': self.currency,
            'payer': self.payer,
            'payee': self.payee,
            'note': self.note,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'type': self.transaction_type
        }


@dataclass
class UserProfile:
    """User profile for PhonePe-style app"""
    user_id: str
    name: str
    phone: str
    email: str
    upi_id: str
    balance: Decimal
    currency: str
    created_at: datetime
    transaction_count: int = 0
    total_sent: Decimal = Decimal('0')
    total_received: Decimal = Decimal('0')


# ============================================================================
# PHONEPE STYLE TRUNCATION ENGINE
# ============================================================================

class PhonePeTruncationEngine:
    """PhonePe-inspired truncation engine with UPI features"""
    
    def __init__(self, currency: str = 'INR', strategy: str = 'down'):
        self.currency = currency
        self.strategy = strategy
        self.decimal_places = 2
        self.rounding_mode = ROUND_DOWN if strategy == 'down' else ROUND_HALF_UP
        
        # UPI-specific features
        self.transaction_fee_percent = Decimal('0.00')  # No fee for UPI
        self.minimum_truncation = Decimal('0.01')
        self.cashback_enabled = False
        self.cashback_rate = Decimal('0.01')  # 1% cashback
        
        # Statistics
        self.stats = {
            'total_truncations': 0,
            'total_loss': Decimal('0'),
            'saved_amount': Decimal('0'),
            'cashback_earned': Decimal('0')
        }
        
        logger.info(f"PhonePe Engine initialized: {currency}, {strategy}")
    
    def truncate(self, amount: Union[int, float, str, Decimal]) -> Decimal:
        """Truncate amount to 2 decimal places"""
        amount_dec = Decimal(str(amount))
        quantize_str = '0.01'
        truncated = amount_dec.quantize(Decimal(quantize_str), rounding=self.rounding_mode)
        
        # Update stats
        loss = amount_dec - truncated
        self.stats['total_truncations'] += 1
        self.stats['total_loss'] += loss
        
        return truncated
    
    def process_payment(self, amount: Decimal, payer: str, payee: str, note: str = "") -> UpiTransaction:
        """Process a payment with truncation"""
        # Truncate amount
        truncated_amount = self.truncate(amount)
        loss = amount - truncated_amount
        
        # Generate UPI transaction ID
        txn_id = f"UPI{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        
        # Create transaction
        transaction = UpiTransaction(
            transaction_id=txn_id,
            amount=amount,
            truncated_amount=truncated_amount,
            loss_amount=loss,
            currency=self.currency,
            payer=payer,
            payee=payee,
            note=note or "Payment via PhonePe",
            status="SUCCESS",
            timestamp=datetime.now(),
            transaction_type="PAYMENT"
        )
        
        # Apply cashback if enabled
        if self.cashback_enabled and loss > 0:
            cashback = loss * self.cashback_rate
            self.stats['cashback_earned'] += cashback
        
        return transaction
    
    def calculate_split(self, amount: Decimal, num_people: int) -> List[Decimal]:
        """Split amount among people with truncation"""
        per_person = amount / Decimal(str(num_people))
        truncated_per_person = self.truncate(per_person)
        
        # Adjust to ensure total matches
        total_truncated = truncated_per_person * Decimal(str(num_people))
        difference = amount - total_truncated
        
        splits = [truncated_per_person] * num_people
        # Add difference to first person
        if difference > 0:
            splits[0] += difference
        
        return splits
    
    def get_statistics(self) -> Dict:
        """Get engine statistics"""
        return {
            'total_truncations': self.stats['total_truncations'],
            'total_loss': float(self.stats['total_loss']),
            'cashback_earned': float(self.stats['cashback_earned']),
            'avg_loss_per_txn': float(self.stats['total_loss'] / max(1, self.stats['total_truncations']))
        }


# ============================================================================
# DATABASE MANAGER (PhonePe Style)
# ============================================================================

class PhonePeDatabase:
    """Database manager for PhonePe-style app"""
    
    def __init__(self, db_path: str = 'phonepe_truncation.db'):
        self.db_path = db_path
        self._init_database()
        self.connection = None
        logger.info(f"PhonePe Database initialized: {db_path}")
    
    def _init_database(self):
        """Initialize database with PhonePe-style schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT,
                upi_id TEXT UNIQUE NOT NULL,
                balance REAL DEFAULT 0,
                currency TEXT DEFAULT 'INR',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                transaction_count INTEGER DEFAULT 0,
                total_sent REAL DEFAULT 0,
                total_received REAL DEFAULT 0
            )
        ''')
        
        # Transactions table (PhonePe style)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT UNIQUE NOT NULL,
                amount REAL NOT NULL,
                truncated_amount REAL NOT NULL,
                loss_amount REAL NOT NULL,
                currency TEXT DEFAULT 'INR',
                payer TEXT NOT NULL,
                payee TEXT NOT NULL,
                note TEXT,
                status TEXT DEFAULT 'SUCCESS',
                transaction_type TEXT DEFAULT 'PAYMENT',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Contacts/Beneficiaries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                contact_phone TEXT NOT NULL,
                contact_name TEXT,
                contact_upi_id TEXT,
                frequency INTEGER DEFAULT 0,
                last_transaction DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Cashback ledger
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cashback_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                transaction_id TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date DATE NOT NULL,
                total_transactions INTEGER,
                total_amount REAL,
                total_loss REAL,
                avg_loss REAL,
                report_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def create_user(self, user: UserProfile) -> bool:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users 
                (user_id, name, phone, email, upi_id, balance, currency, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.user_id, user.name, user.phone, user.email,
                user.upi_id, float(user.balance), user.currency,
                user.created_at.isoformat()
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            logger.error(f"User {user.phone} already exists")
            return False
    
    def get_user(self, phone: str) -> Optional[Dict]:
        """Get user by phone number"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_upi(self, upi_id: str) -> Optional[Dict]:
        """Get user by UPI ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE upi_id = ?", (upi_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def save_transaction(self, transaction: UpiTransaction) -> bool:
        """Save a transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO transactions 
                (transaction_id, amount, truncated_amount, loss_amount, 
                 currency, payer, payee, note, status, transaction_type, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction.transaction_id,
                float(transaction.amount),
                float(transaction.truncated_amount),
                float(transaction.loss_amount),
                transaction.currency,
                transaction.payer,
                transaction.payee,
                transaction.note,
                transaction.status,
                transaction.transaction_type,
                transaction.timestamp.isoformat(),
                json.dumps({})
            ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving transaction: {e}")
            return False
    
    def update_balance(self, phone: str, amount: Decimal, operation: str = 'add') -> bool:
        """Update user balance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        sign = 1 if operation == 'add' else -1
        try:
            cursor.execute('''
                UPDATE users 
                SET balance = balance + ? 
                WHERE phone = ?
            ''', (float(amount) * sign, phone))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating balance: {e}")
            return False
    
    def get_transactions(self, phone: str, limit: int = 20) -> List[Dict]:
        """Get transactions for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE payer = ? OR payee = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (phone, phone, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def add_contact(self, user_id: str, contact_phone: str, contact_name: str = None):
        """Add a contact/beneficiary"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO contacts 
            (user_id, contact_phone, contact_name, frequency)
            VALUES (?, ?, ?, COALESCE(frequency, 0) + 1)
        ''', (user_id, contact_phone, contact_name))
        conn.commit()
    
    def get_contacts(self, user_id: str) -> List[Dict]:
        """Get contacts for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM contacts 
            WHERE user_id = ?
            ORDER BY frequency DESC, last_transaction DESC
        ''', (user_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None


# ============================================================================
# PHONEPE-STYLE APP
# ============================================================================

class PhonePeApp:
    """PhonePe-inspired money truncation application"""
    
    def __init__(self):
        self.db = PhonePeDatabase()
        self.engine = PhonePeTruncationEngine('INR', 'down')
        self.current_user = None
        self.running = True
        
        # Sample users for demo
        self._seed_demo_data()
        
        logger.info("PhonePe App initialized")
    
    def _seed_demo_data(self):
        """Seed demo users"""
        demo_users = [
            {
                'user_id': 'user_001',
                'name': 'Rahul Sharma',
                'phone': '9876543210',
                'email': 'rahul@email.com',
                'upi_id': 'rahul@pay',
                'balance': 50000.00
            },
            {
                'user_id': 'user_002',
                'name': 'Priya Patel',
                'phone': '9876543211',
                'email': 'priya@email.com',
                'upi_id': 'priya@pay',
                'balance': 35000.00
            },
            {
                'user_id': 'user_003',
                'name': 'Amit Kumar',
                'phone': '9876543212',
                'email': 'amit@email.com',
                'upi_id': 'amit@pay',
                'balance': 25000.00
            },
            {
                'user_id': 'user_004',
                'name': 'Sneha Reddy',
                'phone': '9876543213',
                'email': 'sneha@email.com',
                'upi_id': 'sneha@pay',
                'balance': 45000.00
            }
        ]
        
        for user_data in demo_users:
            user = UserProfile(
                user_id=user_data['user_id'],
                name=user_data['name'],
                phone=user_data['phone'],
                email=user_data['email'],
                upi_id=user_data['upi_id'],
                balance=Decimal(str(user_data['balance'])),
                currency='INR',
                created_at=datetime.now()
            )
            self.db.create_user(user)
    
    def login(self):
        """User login"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}🔐 LOGIN TO PHONEPE{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        phone = input(f"\n{Colors.BLUE}Enter Phone Number: {Colors.END}").strip()
        
        user = self.db.get_user(phone)
        if user:
            self.current_user = user
            print(f"\n{Colors.GREEN}✅ Welcome back, {user['name']}!{Colors.END}")
            print(f"   UPI ID: {user['upi_id']}")
            print(f"   Balance: ₹{user['balance']:.2f}")
            return True
        else:
            print(f"\n{Colors.RED}❌ User not found. Please sign up.{Colors.END}")
            return self.signup()
    
    def signup(self):
        """User signup"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}📝 SIGN UP FOR PHONEPE{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        phone = input(f"\n{Colors.BLUE}Phone Number: {Colors.END}").strip()
        
        if self.db.get_user(phone):
            print(f"{Colors.RED}❌ User already exists. Please login.{Colors.END}")
            return False
        
        name = input(f"{Colors.BLUE}Full Name: {Colors.END}").strip()
        email = input(f"{Colors.BLUE}Email: {Colors.END}").strip()
        upi_id = input(f"{Colors.BLUE}Choose UPI ID (e.g., name@pay): {Colors.END}").strip()
        
        # Create user
        user_id = f"user_{random.randint(1000, 9999)}"
        user = UserProfile(
            user_id=user_id,
            name=name,
            phone=phone,
            email=email,
            upi_id=upi_id,
            balance=Decimal('1000.00'),  # Welcome bonus
            currency='INR',
            created_at=datetime.now()
        )
        
        if self.db.create_user(user):
            print(f"\n{Colors.GREEN}✅ Account created successfully!{Colors.END}")
            print(f"   UPI ID: {upi_id}")
            print(f"   Welcome Bonus: ₹1000.00")
            self.current_user = self.db.get_user(phone)
            return True
        else:
            print(f"{Colors.RED}❌ Signup failed. Please try again.{Colors.END}")
            return False
    
    def send_money(self):
        """Send money with truncation"""
        if not self.current_user:
            print(f"{Colors.RED}❌ Please login first{Colors.END}")
            return
        
        print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}💸 SEND MONEY{Colors.END}")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"\nBalance: ₹{self.current_user['balance']:.2f}")
        
        # Get payee
        payee_phone = input(f"\n{Colors.BLUE}Enter payee phone number: {Colors.END}").strip()
        payee = self.db.get_user(payee_phone)
        
        if not payee:
            print(f"{Colors.RED}❌ Payee not found{Colors.END}")
            return
        
        if payee_phone == self.current_user['phone']:
            print(f"{Colors.RED}❌ Cannot send money to yourself{Colors.END}")
            return
        
        print(f"   Payee: {payee['name']} ({payee['upi_id']})")
        
        # Get amount
        try:
            amount = Decimal(input(f"{Colors.BLUE}Enter amount (₹): {Colors.END}"))
            if amount <= 0:
                print(f"{Colors.RED}❌ Amount must be positive{Colors.END}")
                return
            
            if amount > Decimal(str(self.current_user['balance'])):
                print(f"{Colors.RED}❌ Insufficient balance{Colors.END}")
                return
            
            note = input(f"{Colors.BLUE}Add a note (optional): {Colors.END}").strip()
            
            # Process payment with truncation
            transaction = self.engine.process_payment(
                amount=amount,
                payer=self.current_user['phone'],
                payee=payee_phone,
                note=note
            )
            
            # Show truncation effect
            print(f"\n{Colors.YELLOW}📊 Payment Breakdown:{Colors.END}")
            print(f"   Original Amount: ₹{transaction.amount:.2f}")
            print(f"   Truncated Amount: ₹{transaction.truncated_amount:.2f}")
            if transaction.loss_amount > 0:
                print(f"   {Colors.ORANGE}Amount Saved (Loss): ₹{transaction.loss_amount:.2f}{Colors.END}")
            else:
                print(f"   {Colors.GREEN}No truncation loss!{Colors.END}")
            
            # Confirm
            confirm = input(f"\n{Colors.BLUE}Confirm payment of ₹{transaction.truncated_amount:.2f}? (y/n): {Colors.END}").strip().lower()
            
            if confirm == 'y':
                # Update balances
                self.db.update_balance(self.current_user['phone'], -transaction.truncated_amount)
                self.db.update_balance(payee_phone, transaction.truncated_amount)
                
                # Save transaction
                self.db.save_transaction(transaction)
                
                # Add to contacts
                self.db.add_contact(self.current_user['user_id'], payee_phone, payee['name'])
                
                # Refresh current user
                self.current_user = self.db.get_user(self.current_user['phone'])
                
                print(f"\n{Colors.GREEN}✅ Payment Successful!{Colors.END}")
                print(f"   Transaction ID: {transaction.transaction_id}")
                print(f"   To: {payee['name']}")
                print(f"   Amount: ₹{transaction.truncated_amount:.2f}")
                print(f"   New Balance: ₹{self.current_user['balance']:.2f}")
                
                if transaction.loss_amount > 0:
                    print(f"\n{Colors.ORANGE}💡 You saved ₹{transaction.loss_amount:.2f} through truncation!{Colors.END}")
                
            else:
                print(f"\n{Colors.RED}❌ Payment cancelled{Colors.END}")
                
        except ValueError:
            print(f"{Colors.RED}❌ Invalid amount{Colors.END}")
    
    def split_bill(self):
        """Split bill among friends"""
        if not self.current_user:
            print(f"{Colors.RED}❌ Please login first{Colors.END}")
            return
        
        print(f"\n{Colors.MAGENTA}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}🧑‍🤝‍🧑 SPLIT BILL{Colors.END}")
        print(f"{Colors.MAGENTA}{'='*60}{Colors.END}")
        
        try:
            total_amount = Decimal(input(f"{Colors.BLUE}Enter total bill amount: ₹{Colors.END}"))
            num_people = int(input(f"{Colors.BLUE}Enter number of people: {Colors.END}"))
            
            if num_people <= 0:
                print(f"{Colors.RED}❌ Invalid number of people{Colors.END}")
                return
            
            # Calculate split with truncation
            splits = self.engine.calculate_split(total_amount, num_people)
            
            print(f"\n{Colors.YELLOW}📊 Split Details:{Colors.END}")
            print(f"   Total Amount: ₹{total_amount:.2f}")
            print(f"   Per Person (truncated): ₹{splits[0]:.2f}")
            print(f"   Total: ₹{sum(splits):.2f}")
            
            if len(splits) > 1:
                print(f"\n   {Colors.GREEN}Adjusted split for {num_people} people:{Colors.END}")
                for i, split in enumerate(splits, 1):
                    print(f"   Person {i}: ₹{split:.2f}")
            
            # Save split transaction
            note = input(f"\n{Colors.BLUE}Add a note (optional): {Colors.END}").strip()
            
            for i, split in enumerate(splits):
                txn_id = f"SPLIT{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100, 999)}"
                transaction = UpiTransaction(
                    transaction_id=txn_id,
                    amount=split,
                    truncated_amount=split,
                    loss_amount=Decimal('0'),
                    currency='INR',
                    payer=self.current_user['phone'],
                    payee=f"Split_{i+1}",
                    note=note or f"Split bill {i+1}/{num_people}",
                    status="SUCCESS",
                    timestamp=datetime.now(),
                    transaction_type="SPLIT"
                )
                self.db.save_transaction(transaction)
            
            print(f"\n{Colors.GREEN}✅ Bill split saved successfully!{Colors.END}")
            
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input{Colors.END}")
    
    def view_transactions(self):
        """View transaction history"""
        if not self.current_user:
            print(f"{Colors.RED}❌ Please login first{Colors.END}")
            return
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}📊 TRANSACTION HISTORY{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        transactions = self.db.get_transactions(self.current_user['phone'], limit=20)
        
        if not transactions:
            print(f"\n{Colors.YELLOW}No transactions found{Colors.END}")
            return
        
        print(f"\n{Colors.BOLD}Recent Transactions:{Colors.END}")
        print(f"{Colors.BOLD}{'-'*60}{Colors.END}")
        
        for t in transactions:
            is_sent = t['payer'] == self.current_user['phone']
            direction = "📤 Sent" if is_sent else "📥 Received"
            amount_prefix = "-" if is_sent else "+"
            color = Colors.RED if is_sent else Colors.GREEN
            
            print(f"{color}{direction}{Colors.END}")
            print(f"  {t['transaction_id']}")
            print(f"  Amount: {color}{amount_prefix}₹{t['amount']:.2f}{Colors.END}")
            if t['loss_amount'] > 0:
                print(f"  {Colors.ORANGE}💰 Saved: ₹{t['loss_amount']:.2f}{Colors.END}")
            print(f"  Note: {t['note'] or 'N/A'}")
            print(f"  {t['timestamp'][:16]}")
            print(f"{'-'*40}")
    
    def view_contacts(self):
        """View contacts/beneficiaries"""
        if not self.current_user:
            print(f"{Colors.RED}❌ Please login first{Colors.END}")
            return
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}👥 CONTACTS & BENEFICIARIES{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        contacts = self.db.get_contacts(self.current_user['user_id'])
        
        if not contacts:
            print(f"\n{Colors.YELLOW}No contacts yet. Start transacting to add contacts!{Colors.END}")
            return
        
        print(f"\n{Colors.BOLD}Frequent Contacts:{Colors.END}")
        print(f"{'-'*40}")
        for contact in contacts:
            print(f"  {contact['contact_name'] or contact['contact_phone']}")
            print(f"  Phone: {contact['contact_phone']}")
            print(f"  Frequency: {contact['frequency']} transactions")
            print(f"{'-'*40}")
    
    def view_statistics(self):
        """View truncation statistics"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}📊 TRUNCATION STATISTICS{Colors.END}")
        print(f"{Colors.HEADER}{'='*60}{Colors.END}")
        
        stats = self.engine.get_statistics()
        
        print(f"\n{Colors.YELLOW}Engine Statistics:{Colors.END}")
        print(f"  Total Transactions: {stats['total_truncations']}")
        print(f"  Total Loss/Saved: ₹{stats['total_loss']:.2f}")
        print(f"  Average Loss per Transaction: ₹{stats['avg_loss_per_txn']:.2f}")
        print(f"  Cashback Earned: ₹{stats['cashback_earned']:.2f}")
        
        # Get transactions for user
        if self.current_user:
            transactions = self.db.get_transactions(self.current_user['phone'], limit=100)
            if transactions:
                total_sent = sum(t['amount'] for t in transactions if t['payer'] == self.current_user['phone'])
                total_received = sum(t['amount'] for t in transactions if t['payee'] == self.current_user['phone'])
                total_loss = sum(t['loss_amount'] for t in transactions)
                
                print(f"\n{Colors.CYAN}User Statistics:{Colors.END}")
                print(f"  Total Sent: ₹{total_sent:.2f}")
                print(f"  Total Received: ₹{total_received:.2f}")
                print(f"  Total Loss Saved: ₹{total_loss:.2f}")
                print(f"  Net Balance: ₹{self.current_user['balance']:.2f}")
                
                if total_sent > 0:
                    savings_rate = (total_loss / total_sent) * 100
                    print(f"  Savings Rate: {savings_rate:.2f}%")
    
    def toggle_cashback(self):
        """Toggle cashback feature"""
        self.engine.cashback_enabled = not self.engine.cashback_enabled
        status = "ON" if self.engine.cashback_enabled else "OFF"
        print(f"\n{Colors.GREEN}✅ Cashback feature turned {status}{Colors.END}")
        if self.engine.cashback_enabled:
            print(f"   Cashback Rate: {float(self.engine.cashback_rate * 100)}%")
    
    def show_dashboard(self):
        """Show user dashboard"""
        if not self.current_user:
            print(f"{Colors.RED}❌ Please login first{Colors.END}")
            return
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}🏠 DASHBOARD{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        print(f"\n{Colors.GREEN}Welcome, {self.current_user['name']}!{Colors.END}")
        print(f"   UPI ID: {self.current_user['upi_id']}")
        print(f"   Phone: {self.current_user['phone']}")
        print(f"   Balance: {Colors.BOLD}₹{self.current_user['balance']:.2f}{Colors.END}")
        
        # Recent transactions
        transactions = self.db.get_transactions(self.current_user['phone'], limit=5)
        if transactions:
            print(f"\n{Colors.YELLOW}Recent Activity:{Colors.END}")
            for t in transactions[:3]:
                is_sent = t['payer'] == self.current_user['phone']
                direction = "→" if is_sent else "←"
                color = Colors.RED if is_sent else Colors.GREEN
                print(f"  {color}{direction} ₹{t['amount']:.2f}{Colors.END} {t['timestamp'][:16]}")
    
    def show_help(self):
        """Show help menu"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}❓ HELP & ABOUT{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        print(f"""
{Colors.GREEN}PhonePe-Style Money Truncation App{Colors.END}

{Colors.YELLOW}Features:{Colors.END}
• Send money with automatic truncation (rounding down)
• Split bills among friends
• Track transaction history
• View truncation savings
• Contacts/beneficiaries management
• Cashback on truncation losses
• Real-time balance updates

{Colors.YELLOW}How Truncation Works:{Colors.END}
When you send ₹100.99, it's truncated to ₹100.00
The ₹0.99 is saved as truncation benefit

{Colors.YELLOW}Benefits:{Colors.END}
• Save money on every transaction
• Transparent truncation display
• No hidden charges
• UPI-style seamless payments

{Colors.GREEN}Made with ❤️ using Python{Colors.END}
""")
    
    def main_menu(self):
        """Display main menu"""
        if not self.current_user:
            print(f"\n{Colors.RED}❌ Please login first{Colors.END}")
            return
        
        while True:
            print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
            print(f"{Colors.BOLD}PHONEPE - MONEY TRUNCATION{Colors.END}")
            print(f"{Colors.CYAN}{'='*60}{Colors.END}")
            print(f"\n{Colors.GREEN}👤 {self.current_user['name']}{Colors.END}")
            print(f"💰 Balance: ₹{self.current_user['balance']:.2f}")
            
            print(f"\n{Colors.BOLD}Choose an option:{Colors.END}")
            print(" 1. 💸 Send Money")
            print(" 2. 🧑‍🤝‍🧑 Split Bill")
            print(" 3. 📊 View Transactions")
            print(" 4. 👥 Contacts")
            print(" 5. 📈 Statistics")
            print(" 6. 🎁 Toggle Cashback")
            print(" 7. 🏠 Dashboard")
            print(" 8. ❓ Help")
            print(" 9. 🚪 Logout")
            print(" 0. ❌ Exit")
            print(f"{Colors.CYAN}{'='*60}{Colors.END}")
            
            choice = input(f"\n{Colors.BLUE}Enter your choice: {Colors.END}").strip()
            
            if choice == '1':
                self.send_money()
            elif choice == '2':
                self.split_bill()
            elif choice == '3':
                self.view_transactions()
            elif choice == '4':
                self.view_contacts()
            elif choice == '5':
                self.view_statistics()
            elif choice == '6':
                self.toggle_cashback()
            elif choice == '7':
                self.show_dashboard()
            elif choice == '8':
                self.show_help()
            elif choice == '9':
                self.current_user = None
                print(f"\n{Colors.GREEN}✅ Logged out successfully{Colors.END}")
                break
            elif choice == '0':
                self.running = False
                break
            else:
                print(f"{Colors.RED}❌ Invalid choice{Colors.END}")
    
    def run(self):
        """Run the application"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}     💰 PHONEPE - MONEY TRUNCATION APP 💰{Colors.END}")
        print(f"{Colors.HEADER}{'='*60}{Colors.END}")
        print(f"\n{Colors.YELLOW}✨ Save money with every transaction!{Colors.END}")
        print(f"   Your money, truncated for your benefit.\n")
        
        while self.running:
            if not self.current_user:
                print(f"\n{Colors.CYAN}{'='*40}{Colors.END}")
                print(f"{Colors.BOLD}📱 PHONEPE{Colors.END}")
                print(f"{Colors.CYAN}{'='*40}{Colors.END}")
                print(" 1. 🔐 Login")
                print(" 2. 📝 Sign Up")
                print(" 0. ❌ Exit")
                print(f"{Colors.CYAN}{'='*40}{Colors.END}")
                
                choice = input(f"\n{Colors.BLUE}Enter your choice: {Colors.END}").strip()
                
                if choice == '1':
                    self.login()
                elif choice == '2':
                    self.signup()
                elif choice == '0':
                    self.running = False
                    break
                else:
                    print(f"{Colors.RED}❌ Invalid choice{Colors.END}")
            else:
                self.main_menu()
        
        # Cleanup
        self.db.close()
        print(f"\n{Colors.HEADER}👋 Thank you for using PhonePe Truncation!{Colors.END}")
        print(f"{Colors.YELLOW}💡 Total saved: ₹{self.engine.stats['total_loss']:.2f}{Colors.END}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    try:
        app = PhonePeApp()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Application terminated by user{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Fatal error: {e}{Colors.END}")
        logger.error(f"Fatal error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
