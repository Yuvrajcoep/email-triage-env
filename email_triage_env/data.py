"""Ticket data with ground-truth labels for all three tasks."""

TASK1_TICKETS = [
    {
        "ticket": {
            "ticket_id": "TKT-101",
            "subject": "URGENT: Production server completely unresponsive - 3 hours down",
            "body": (
                "Our main production server has been completely unresponsive for 3 hours. "
                "All customer-facing services are down: website, mobile app, and internal tools. "
                "We're losing approximately $50,000 per hour. 500+ active customers cannot access "
                "our platform. Error logs show: 'Connection refused on port 443' and "
                "'Database connection pool exhausted'. This is a P0 incident. Please respond immediately."
            ),
            "sender_name": "Sarah Chen",
            "sender_email": "cto@acmecorp.com",
            "created_at": "2024-01-15T09:00:00Z",
            "previous_interactions": [],
            "metadata": {"company_tier": "enterprise", "mrr": 50000},
        },
        "ground_truth": {"category": "technical", "urgency": "critical"},
    },
    {
        "ticket": {
            "ticket_id": "TKT-102",
            "subject": "Charged twice for January subscription",
            "body": (
                "Hi, I noticed I was charged twice for my January subscription. My credit card "
                "ending in 4242 shows two charges of $99.00 on January 3rd (transaction IDs: "
                "TXN-4521 and TXN-4522). Could you please refund the duplicate charge? "
                "My account email is john.doe@example.com. Thank you, John"
            ),
            "sender_name": "John Doe",
            "sender_email": "john.doe@example.com",
            "created_at": "2024-01-15T10:30:00Z",
            "previous_interactions": [],
            "metadata": {"subscription_tier": "pro"},
        },
        "ground_truth": {"category": "billing", "urgency": "medium"},
    },
    {
        "ticket": {
            "ticket_id": "TKT-103",
            "subject": "Cannot access account - locked after password reset",
            "body": (
                "Hello Support, I tried to reset my password yesterday but after resetting it "
                "I keep getting 'Your account has been temporarily locked'. I've waited 24 hours "
                "but still locked. I need access urgently as I have a client presentation tomorrow "
                "that uses materials stored in my account. Account email: maria.garcia@company.com. "
                "Please help ASAP! Best, Maria"
            ),
            "sender_name": "Maria Garcia",
            "sender_email": "maria.garcia@company.com",
            "created_at": "2024-01-15T11:00:00Z",
            "previous_interactions": ["2024-01-14: User submitted password reset request"],
            "metadata": {"account_age_days": 365},
        },
        "ground_truth": {"category": "account", "urgency": "high"},
    },
    {
        "ticket": {
            "ticket_id": "TKT-104",
            "subject": "Order #45892 not delivered after 2 weeks",
            "body": (
                "I placed order #45892 on December 29th and was promised delivery by January 5th. "
                "It is now January 15th and I still haven't received my package. Tracking number "
                "TRK-789456 shows 'In Transit' since January 3rd with no updates. "
                "This was a birthday gift and the birthday has now passed. I would like either "
                "a replacement shipment with express delivery or a full refund. Order value: $127.50. "
                "Please respond, Robert Kim"
            ),
            "sender_name": "Robert Kim",
            "sender_email": "robert.kim@personal.com",
            "created_at": "2024-01-15T14:00:00Z",
            "previous_interactions": [],
            "metadata": {"order_value": 127.50},
        },
        "ground_truth": {"category": "shipping", "urgency": "medium"},
    },
    {
        "ticket": {
            "ticket_id": "TKT-105",
            "subject": "Question about upgrading to Enterprise plan - pricing inquiry",
            "body": (
                "Hi, our team has been using the Professional plan for 6 months and we're very happy. "
                "We're growing and thinking about upgrading to Enterprise. Could you send information about: "
                "1) Enterprise plan pricing for ~50 users, 2) Additional features included, "
                "3) Whether we can get a demo of the advanced analytics dashboard, "
                "4) Volume discounts for annual billing. No rush - just exploring for Q2 planning. Thanks, Amanda"
            ),
            "sender_name": "Amanda Foster",
            "sender_email": "amanda.foster@techstartup.io",
            "created_at": "2024-01-15T15:00:00Z",
            "previous_interactions": [],
            "metadata": {"current_plan": "professional", "team_size": 50},
        },
        "ground_truth": {"category": "general", "urgency": "low"},
    },
]

TASK2_TICKETS = [
    {
        "ticket": {
            "ticket_id": "TKT-201",
            "subject": "Critical: SQL injection vulnerability in login endpoint",
            "body": (
                "Our security team discovered a critical SQL injection vulnerability in your "
                "/api/login endpoint. We bypassed authentication using: username: admin'-- "
                "This affects all versions below 3.5.2. We have documented this as CVE-2024-12345 "
                "and are giving 72 hours to patch before public disclosure. "
                "We are a paying enterprise customer and expect immediate action."
            ),
            "sender_name": "Alex Rivera",
            "sender_email": "security@techcorp.com",
            "created_at": "2024-01-15T08:00:00Z",
            "previous_interactions": [],
            "metadata": {"account_type": "enterprise"},
        },
        "ground_truth": {
            "department": "tech_support",
            "required_keywords": ["security", "vulnerability", "patch", "urgent", "72"],
        },
    },
    {
        "ticket": {
            "ticket_id": "TKT-202",
            "subject": "Fraudulent charge - did not authorize $899 payment",
            "body": (
                "URGENT - I received an email confirming a $899 charge for 'Enterprise Annual Upgrade' "
                "which I absolutely did not authorize. I never requested this upgrade. "
                "Please immediately: 1) Reverse this charge, 2) Downgrade me back to Pro plan, "
                "3) Investigate how this happened. I will dispute with my credit card if not resolved "
                "within 24 hours. - Jennifer Walsh"
            ),
            "sender_name": "Jennifer Walsh",
            "sender_email": "jennifer.walsh@gmail.com",
            "created_at": "2024-01-15T09:30:00Z",
            "previous_interactions": [],
            "metadata": {"charge_amount": 899, "account_type": "pro"},
        },
        "ground_truth": {
            "department": "billing_team",
            "required_keywords": ["refund", "investigate", "apologize", "24"],
        },
    },
    {
        "ticket": {
            "ticket_id": "TKT-203",
            "subject": "Corporate account transfer - company acquisition",
            "body": (
                "Our company Acme Corp has been acquired by GlobalTech Inc. effective February 1st. "
                "We need to transfer our enterprise account (Account ID: ENT-4521, 200+ users) "
                "to the new parent company. This involves: transferring billing, updating account owner, "
                "migrating all data and permissions, signing a new enterprise agreement. "
                "Please assign a dedicated account manager for this transition."
            ),
            "sender_name": "Jane Smith",
            "sender_email": "jane.smith@acme.com",
            "created_at": "2024-01-15T10:00:00Z",
            "previous_interactions": [],
            "metadata": {"account_size": 200, "account_type": "enterprise"},
        },
        "ground_truth": {
            "department": "account_management",
            "required_keywords": ["account manager", "transition", "migration", "agreement"],
        },
    },
    {
        "ticket": {
            "ticket_id": "TKT-204",
            "subject": "15 of 20 boxes arrived completely crushed",
            "body": (
                "I received my bulk order (Order #ORD-89234) today and 15 out of 20 boxes are completely "
                "crushed, products inside are damaged. The outer cartons were clearly dropped or had "
                "heavy items stacked on them. Photos attached (IMG_001 through IMG_015). "
                "Order value: $3,450. I need either: replacement of the 15 damaged boxes ASAP "
                "(customers waiting) or a full refund for the damaged items. "
                "Not acceptable for a business order. Tom Bradley, Bradley's Hardware Store"
            ),
            "sender_name": "Tom Bradley",
            "sender_email": "tom@bradleyshardware.com",
            "created_at": "2024-01-15T11:30:00Z",
            "previous_interactions": [],
            "metadata": {"order_value": 3450, "damaged_quantity": 15, "total_quantity": 20},
        },
        "ground_truth": {
            "department": "logistics",
            "required_keywords": ["replacement", "damage", "claim", "apologize", "refund"],
        },
    },
    {
        "ticket": {
            "ticket_id": "TKT-205",
            "subject": "Feature request: Bulk CSV export with custom date ranges",
            "body": (
                "Hi, I'm a 3-year user and would love to see bulk CSV export functionality added "
                "to the analytics dashboard. Specifically: custom date ranges for export, "
                "export multiple metrics at once, scheduled/automated exports, and multiple formats "
                "(CSV, Excel, JSON). This would save our data team ~4 hours per week. "
                "Happy to join a beta program. Best, Patricia Liu"
            ),
            "sender_name": "Patricia Liu",
            "sender_email": "p.liu@datacompany.com",
            "created_at": "2024-01-15T13:00:00Z",
            "previous_interactions": [],
            "metadata": {"customer_age_years": 3, "account_type": "professional"},
        },
        "ground_truth": {
            "department": "general_support",
            "required_keywords": ["thank", "feedback", "product", "roadmap", "beta"],
        },
    },
]

TASK3_TICKETS = [
    {
        "ticket": {
            "ticket_id": "TKT-301",
            "subject": "CRITICAL SLA BREACH: Enterprise client down 6+ hours",
            "body": (
                "This is a Severity-1 incident. Enterprise client NationalBank Corp (Account: ENT-001, "
                "$2M ARR) has been experiencing a complete platform outage for 6+ hours, breaching their "
                "contracted 99.99% SLA. Impact: 5,000 bank employees offline, real-time transaction "
                "processing blocked, regulatory reporting offline. Financial penalties estimated $500K. "
                "Root cause suspected: Database cluster failover failure. "
                "Executive sponsor CTO Patricia Chen has personally contacted our CEO."
            ),
            "sender_name": "David Park",
            "sender_email": "d.park@nationalbank.com",
            "created_at": "2024-01-15T06:00:00Z",
            "previous_interactions": [
                "06:00 - Initial report filed",
                "07:00 - Tech support assigned",
                "08:00 - Issue persists, escalation requested",
            ],
            "metadata": {"arr": 2000000, "sla_breach": True, "hours_down": 6},
        },
        "ground_truth": {
            "category": "technical",
            "urgency": "critical",
            "department": "tech_support",
            "requires_escalation": True,
            "resolution_keywords": ["sla", "compensation", "root cause", "prevention"],
        },
    },
    {
        "ticket": {
            "ticket_id": "TKT-302",
            "subject": "Account hacked - unauthorized logins from Russia and China",
            "body": (
                "EMERGENCY - My account has been compromised! Alerts show logins from: "
                "Russia (Moscow): 3 logins between 2am-4am, China (Beijing): 1 login at 5am. "
                "I have never been to these countries. All my API keys, private projects, and "
                "client data may be exposed. I'm a freelance developer - all client code is stored here. "
                "Please: 1) Terminate all active sessions, 2) Lock account, "
                "3) Audit what was accessed/downloaded. Carlos Mendez"
            ),
            "sender_name": "Carlos Mendez",
            "sender_email": "carlos.mendez@freelance.dev",
            "created_at": "2024-01-15T07:30:00Z",
            "previous_interactions": [],
            "metadata": {"account_type": "professional", "data_sensitivity": "high"},
        },
        "ground_truth": {
            "category": "account",
            "urgency": "critical",
            "department": "account_management",
            "requires_escalation": True,
            "resolution_keywords": ["session", "secured", "audit", "breach"],
        },
    },
    {
        "ticket": {
            "ticket_id": "TKT-303",
            "subject": "Refund request - annual plan purchased by mistake",
            "body": (
                "Hi, I accidentally purchased the annual Business plan instead of monthly Professional "
                "plan yesterday. I clicked the wrong button. I paid $1,188 (annual) but only wanted "
                "$99/month. Can I please get a refund and switch to monthly billing? "
                "Transaction ID: TXN-9876, Purchase date: January 14, 2024. Thanks, Laura Chen"
            ),
            "sender_name": "Laura Chen",
            "sender_email": "laura.chen@startup.com",
            "created_at": "2024-01-15T09:00:00Z",
            "previous_interactions": [],
            "metadata": {"purchase_amount": 1188, "days_since_purchase": 1},
        },
        "ground_truth": {
            "category": "billing",
            "urgency": "medium",
            "department": "billing_team",
            "requires_escalation": False,
            "resolution_keywords": ["refund", "plan", "confirm"],
        },
    },
    {
        "ticket": {
            "ticket_id": "TKT-304",
            "subject": "GDPR Right to Erasure - Immediate account deletion required",
            "body": (
                "To the Data Protection Officer, under Article 17 of the GDPR (Right to Erasure), "
                "I formally request deletion of all my personal data: account information, usage data "
                "and logs, all content created or uploaded, any data shared with third-party processors. "
                "Per GDPR you have 30 days to comply. I request written confirmation. "
                "My account: elizabeth.mueller@example.de, Account ID: USR-77823. "
                "Sincerely, Elizabeth Müller (EU resident)"
            ),
            "sender_name": "Elizabeth Müller",
            "sender_email": "elizabeth.mueller@example.de",
            "created_at": "2024-01-15T10:00:00Z",
            "previous_interactions": [],
            "metadata": {"region": "EU", "request_type": "gdpr_erasure", "legal_deadline_days": 30},
        },
        "ground_truth": {
            "category": "account",
            "urgency": "high",
            "department": "account_management",
            "requires_escalation": True,
            "resolution_keywords": ["gdpr", "deletion", "confirm", "30 days"],
        },
    },
    {
        "ticket": {
            "ticket_id": "TKT-305",
            "subject": "Dashboard loads very slowly - 45 second page loads",
            "body": (
                "Hello, our analytics dashboard has been very slow for the past week. Pages that "
                "loaded in under 2 seconds now take 45-60 seconds, sometimes timing out. "
                "This affects our daily morning standup. We're managing by using old screenshots. "
                "Browser: Chrome 120. Account: Company Pro Plan. All 12 users experiencing same issue. "
                "Best, Kevin O'Brien"
            ),
            "sender_name": "Kevin O'Brien",
            "sender_email": "kevin.obrien@mediaco.com",
            "created_at": "2024-01-15T11:00:00Z",
            "previous_interactions": ["Jan 8: Similar slow performance reported, resolved itself"],
            "metadata": {"account_type": "professional", "affected_users": 12},
        },
        "ground_truth": {
            "category": "technical",
            "urgency": "medium",
            "department": "tech_support",
            "requires_escalation": False,
            "resolution_keywords": ["investigating", "performance", "fix", "update"],
        },
    },
    {
        "ticket": {
            "ticket_id": "TKT-306",
            "subject": "Partnership inquiry - white-label for 10,000 customers",
            "body": (
                "Hello, I'm VP of Product at RetailOS Inc., a POS software company with 10,000 retail "
                "customers. We're interested in white-labeling your analytics platform for our customers. "
                "Specifics: 10,000 end customers, monthly revenue share preferred, custom branding and "
                "SSO integration needed, interested in reseller agreement. "
                "Could you connect me with your partnerships/enterprise sales team? "
                "Steve Morrison, VP Product, RetailOS Inc."
            ),
            "sender_name": "Steve Morrison",
            "sender_email": "s.morrison@retailos.com",
            "created_at": "2024-01-15T12:00:00Z",
            "previous_interactions": [],
            "metadata": {"potential_customer_count": 10000},
        },
        "ground_truth": {
            "category": "general",
            "urgency": "medium",
            "department": "account_management",
            "requires_escalation": False,
            "resolution_keywords": ["partnership", "sales", "connect", "follow"],
        },
    },
    {
        "ticket": {
            "ticket_id": "TKT-307",
            "subject": "API rate limit causing production failures - need immediate increase",
            "body": (
                "Our production system is failing because we're hitting your API rate limit of "
                "1,000 requests/minute. We're a financial data platform with legitimate, predictable usage. "
                "Current situation: ~15% of requests get HTTP 429 errors, causing calculation errors in "
                "our financial models, our clients' trading decisions depend on this data. "
                "We need rate limit increased to 10,000 requests/minute immediately. "
                "We're on Enterprise plan paying $15,000/month. James Liu, CTO FinanceFlow"
            ),
            "sender_name": "James Liu",
            "sender_email": "james.liu@financeflow.io",
            "created_at": "2024-01-15T13:00:00Z",
            "previous_interactions": [],
            "metadata": {"mrr": 15000, "account_type": "enterprise", "requested_limit": 10000},
        },
        "ground_truth": {
            "category": "technical",
            "urgency": "high",
            "department": "tech_support",
            "requires_escalation": False,
            "resolution_keywords": ["rate limit", "increase", "approved", "timeline"],
        },
    },
    {
        "ticket": {
            "ticket_id": "TKT-308",
            "subject": "Question about importing data from Salesforce",
            "body": (
                "Hi, I'm evaluating your platform and want to understand if I can import our existing "
                "Salesforce data. Specifically: 1) Native Salesforce connector? 2) What data can be "
                "imported (contacts, deals, activities)? 3) Real-time or batch sync? "
                "4) Any additional cost for the integration? I'm on a free trial (expires Jan 25). "
                "Thanks, Nina Patel"
            ),
            "sender_name": "Nina Patel",
            "sender_email": "nina.patel@consultingco.com",
            "created_at": "2024-01-15T14:00:00Z",
            "previous_interactions": [],
            "metadata": {"account_type": "trial", "trial_expires": "2024-01-25"},
        },
        "ground_truth": {
            "category": "general",
            "urgency": "low",
            "department": "general_support",
            "requires_escalation": False,
            "resolution_keywords": ["salesforce", "integration", "connector", "documentation"],
        },
    },
]
