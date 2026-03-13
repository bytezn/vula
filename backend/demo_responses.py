"""Demo response engine for Pfula — used when no API key is available.

Provides realistic, pre-crafted responses for the stage demo scenarios
so the UI can be demonstrated without a live Claude connection.
"""

import asyncio
import re

DEMO_RESPONSES = {
    "sassa": """I can help with your **SASSA SRD grant**. Let me walk you through this.

**Common reasons for SRD rejection:**
- Income above R625/month detected via bank account checks
- Receiving another grant (child support counts as income)
- UIF payments detected
- NSFAS funding detected (if you're a student)
- Employment records in the system (even after retrenchment)

**What to do right now:**

1. **Check your status** at srd.sassa.gov.za — it should show the specific reason for decline
2. **If the reason is wrong**, you can **appeal within 90 days**:
   - Go to srd.sassa.gov.za → Appeal section
   - Upload proof that the rejection reason doesn't apply to you
   - For example: if it says you're employed but you were retrenched, upload your retrenchment letter

3. **If your appeal is rejected**, you can escalate to the **Independent Tribunal for Social Assistance Appeals (ITSAA)**

**Your rights:**
- Section 27(1)(c) of the Constitution guarantees the right to social security
- SASSA must give you **written reasons** for any rejection
- The application is always **FREE** — never pay anyone

**SASSA toll-free:** 0800 60 10 11

Would you like me to help you draft an appeal, or do you need directions to your nearest SASSA office?""",

    "home_affairs": """I understand the frustration — **8 months is unreasonably long** for a Smart ID application. Here's exactly what to do:

**Your situation:** You applied, had biometrics taken, and have a receipt with a reference number. The office keeps saying "still processing."

**Step-by-step escalation:**

1. **Check status online first:** Go to www.dha.gov.za/index.php/id-status or call **0800 60 11 90** with your reference number

2. **If "still processing"** — go back to the office and ask to speak to the **Office Manager** (not the counter staff). Show your receipt and state clearly: "My application has been pending for 8 months. I need this resolved today."

3. **If the office doesn't help** — contact the **Provincial Manager for KwaZulu-Natal** via the DHA call centre

4. **If still no response** — lodge a complaint on the **Presidential Hotline: 17737**

5. **Nuclear option** — lodge a complaint with the **Public Protector: 0800 11 20 40**

**Your legal rights:**
- **Section 33 of the Constitution**: you have the right to administrative action that is lawful, reasonable, and procedurally fair
- Courts have found that **3+ months is unreasonable** for an ID application
- Under the **Promotion of Administrative Justice Act (PAJA)**, you can challenge unreasonable delays

**For your job application:** Ask the employer if they'll accept a **temporary ID printout** from Home Affairs while you wait for the Smart ID card. Most employers will.

**Nearest offices in Durban:**
- **Umhlanga (Gateway)**: Usually shorter queues, Saturday service available
- **Durban CBD (Field Street)**: Arrive before 07:00

Would you like me to **draft a formal complaint letter** to the Director General of Home Affairs? I can cite the specific legislation and include your reference number.""",

    "municipal": """A **triple increase** in your rates bill is almost certainly an error. Let me help you figure this out.

**Most likely causes:**

1. **Estimated reading used instead of actual meter reading** — this is the #1 reason for sudden spikes. Check your bill: if it says "E" next to the reading, it's estimated.

2. **Municipal revaluation** increased your property value — this happens every 4 years.

3. **Billing error** — it happens more often than it should.

**What to do right now:**

1. **Read your actual meter** — write down the number on your electricity and water meters right now
2. **Compare with the bill** — if the bill shows a higher reading than your actual meter, they've estimated incorrectly
3. **Go to your nearest eThekwini Customer Care Centre** with:
   - Your bill
   - A photo of your actual meter reading
   - Your ID
   - Ask them to correct the reading and recalculate

**If they estimated:** They must recalculate based on your actual reading. You only pay for what you used.

**If it's a property revaluation:** You can **object** during the next General Valuation period under the **Municipal Property Rates Act 6 of 2004**.

**About disconnection:**
- eThekwini **may NOT disconnect water** to residential properties for non-payment (Constitutional Court ruling)
- They **must offer a payment arrangement** before disconnection of electricity
- Ask about the **indigent subsidy** if your household income is below R4,500/month — you qualify for free basic services

**eThekwini Customer Care:**
- **CBD:** Florence Mkhize Building, 251 Anton Lembede Street
- **Call:** 080 131 3013 (toll-free)
- **Hours:** Mon–Fri 07:30–16:00

Don't pay the inflated bill yet. Get the correction first. Would you like help with anything else?""",

    "sars": """Congratulations on the new job! Filing your first tax return is easier than it looks. I'll walk you through every step.

**Step 1: Register with SARS**
- Go to **www.sarsefiling.co.za** and click "Register"
- You'll need your **ID number** and a **valid email address**
- SARS will send you a **tax reference number** — save this forever

**Step 2: Get your IRP5 certificate**
- This comes from your **employer's HR/payroll department**
- It shows your total earnings and tax already deducted
- Ask for it — they're required to provide it

**Step 3: File your return**
- Log in to eFiling during **tax season** (July–November)
- Your IRP5 should be **pre-populated** — check the numbers match your payslips
- If everything looks right, just click submit

**Step 4: Check your assessment**
- SARS will issue an assessment within a few days
- If they **owe you money** (you were over-taxed), the refund goes to your bank account
- If **you owe them**, you can apply for a payment arrangement

**Important for first-timers:**
- If you earn **below R95,750/year** from a single employer, you may not even need to file
- But if tax was deducted from your salary, **file anyway** — you might get a refund!
- Keep all your **payslips** as proof
- **Medical aid tax credits** are automatic if your employer reported them

**You do NOT need:**
- An accountant (for a basic salary return)
- To visit a SARS office (everything is online)
- To pay anyone to "help" you file

**SARS Help:** 0800 00 7277 (toll-free)
**eFiling:** www.sarsefiling.co.za

Any specific questions about the process?""",

    "zulu": """Sawubona! Ngiyakuzwa, futhi ngizokusiza.

**Uma umama wakho engayitholanga imali yakhe yempesheni (Older Persons Grant):**

1. **Shayela i-SASSA** ku-**0800 60 10 11** (mahhala) — bacele bahlole ukuthi kwenzenjani nge-akhawunti yakhe

2. **Iya ehhovisi le-SASSA eliseduze** nalezi zinto:
   - I-ID kamama wakho
   - Iphepha lokubhalisa (receipt) uma likhona
   - I-bank statement yakhe (3 izinyanga)

3. **Izimbangela ezivamile zokungakhokhelwa:**
   - I-akhawunti yasebhange ishintshile noma ivaliwe
   - I-SASSA idinga ukuqinisekisa (verification)
   - Kukhona iphutha ohlelweni (system error)

**Amalungelo kamama wakho:**
- USection 27(1)(c) woMthethosisekelo uthi wonke umuntu unelungelo lokuvikelwa emphakathini
- I-SASSA **kufanele ikhokhe** ngesikhathi — uma iphuzile, kufanele ikhokhele izinyanga eziphuthelwe (back-pay)

**Amahhovisi e-SASSA eThekwini:**
- **Umlazi:** V Section, Umlazi Mega City
- **KwaMashu:** KwaMashu Civic Centre, D Section
- **Chatsworth:** Unit 12, Chatsworth Centre

**Inombolo yasimahla:** 0800 60 10 11

Ungakhathazeki — sizokusiza umama wakho athole imali yakhe. Kukhona okunye ongathanda ukukubuza?""",

    "escalation": """I'll draft that formal complaint letter for you right now.

---

**FORMAL COMPLAINT — UNREASONABLE DELAY IN PROCESSING SMART ID APPLICATION**

**To:** The Director General, Department of Home Affairs
**From:** Thandi Nkosi (ID: 8501015009081)
**Date:** 13 March 2026
**Reference:** DUR-2025-44891

**Dear Director General,**

I write to formally complain about the unreasonable and unlawful delay in processing my Smart ID Card application.

**Facts:**
1. I submitted my application at the Home Affairs office in Durban on approximately May 2025 (Reference: DUR-2025-44891).
2. My biometrics were captured and I was issued a receipt.
3. As of the date of this letter — more than **10 months later** — my application remains unprocessed.
4. I have visited the office on three separate occasions and contacted the DHA hotline. On each occasion I was told the application is "still processing" with no explanation for the delay.

**Legal basis:**
- **Section 33 of the Constitution** guarantees the right to administrative action that is lawful, reasonable, and procedurally fair.
- The **Promotion of Administrative Justice Act (PAJA), Act 3 of 2000** requires that administrative action be taken within a reasonable time.
- South African courts have consistently held that delays exceeding 3 months in processing identity documents are unreasonable.

**Relief sought:**
I request that my Smart ID Card application (Ref: DUR-2025-44891) be processed and my card made available for collection **within 14 business days** of receipt of this letter.

Failing this, I reserve my right to:
1. Approach the **Public Protector** under Section 182 of the Constitution
2. Seek relief from the **High Court** by way of a mandamus order compelling the Department to process my application

**Yours faithfully,**
Thandi Nkosi
ID: 8501015009081
Contact: [your phone number]

---

This letter is ready to send. You can:
- **Print it** and deliver it in person to the Home Affairs office (get a receipt!)
- **Email it** to the DHA Director General's office
- **Send a copy** to the Public Protector at the same time for added pressure

Would you like me to create a tracking case for this so we can follow up?""",

    "default": """I can help with that! I'm knowledgeable about these South African government services:

- **SASSA** — grants, appeals, applications
- **Home Affairs** — IDs, passports, birth certificates
- **UIF** — unemployment, maternity, illness benefits
- **SARS** — tax returns, VAT, clearance certificates
- **eThekwini Municipal** — rates, water, electricity, housing
- **Deeds Office** — title deeds, property transfers
- **CIPC** — company registration, trademarks

Could you tell me more about what you need? The more specific you are, the better I can help. For example:
- "My SASSA grant was rejected"
- "I need a Smart ID card"
- "My municipal bill seems wrong"
- "How do I file my first tax return?"

I'm here to guide you step by step. 🤝"""
}


def get_demo_response(message: str) -> str:
    """Match a user message to the best demo response."""
    text = message.lower()

    if any(w in text for w in ["sawubona", "umama", "isicelo", "isibonelelo", "ngicela", "imali"]):
        return DEMO_RESPONSES["zulu"]

    if any(w in text for w in ["sassa", "grant", "srd", "r370", "rejected", "declined", "child support"]):
        return DEMO_RESPONSES["sassa"]

    if any(w in text for w in ["home affairs", "smart id", "id card", "passport", "8 month", "birth certificate"]):
        return DEMO_RESPONSES["home_affairs"]

    if any(w in text for w in ["municipal", "rates", "bill", "tripled", "water", "electricity", "ethekwini"]):
        return DEMO_RESPONSES["municipal"]

    if any(w in text for w in ["sars", "tax", "first time", "tax return", "efiling", "irp5"]):
        return DEMO_RESPONSES["sars"]

    if any(w in text for w in ["escalat", "complaint", "letter", "formal", "thandi"]):
        return DEMO_RESPONSES["escalation"]

    return DEMO_RESPONSES["default"]


async def stream_demo_response(message: str):
    """Yield demo response chunks to simulate streaming."""
    response = get_demo_response(message)
    # Stream in realistic chunks
    words = response.split(" ")
    chunk = ""
    for i, word in enumerate(words):
        chunk += word + " "
        if len(chunk) > 15 or i == len(words) - 1:
            yield chunk
            chunk = ""
            await asyncio.sleep(0.03)  # Simulate network latency
