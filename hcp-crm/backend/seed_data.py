"""
Seed script — inserts rich sample data into the interactions table.
Run from backend/ folder:
    python seed_data.py

Covers:
  - 6 Positive sentiment interactions (with upcoming follow-ups)
  - 4 Negative sentiment interactions
  - 4 Neutral sentiment interactions
  - Multiple upcoming follow-up dates
  - Varied specialties, hospitals, products, interaction types
"""
import sys
import os
from datetime import datetime, timedelta, timezone

# Make sure app package is importable
sys.path.insert(0, os.path.dirname(__file__))

from app.database.connection import get_engine, create_tables
from app.models.interaction import Interaction
from sqlalchemy.orm import sessionmaker

# ── helpers ──────────────────────────────────────────────────────────────────

def now():
    return datetime.now(timezone.utc)

def days_ago(n):
    return now() - timedelta(days=n)

def days_from_now(n):
    return now() + timedelta(days=n)

# ── sample records ────────────────────────────────────────────────────────────

SAMPLES = [

    # ── POSITIVE SENTIMENT (6 records) ───────────────────────────────────────

    {
        "hcp_name": "Dr. Priya Rao",
        "specialty": "Endocrinology",
        "hospital": "Apollo Hospital, Hyderabad",
        "interaction_type": "Visit",
        "datetime": days_ago(2),
        "products": "Januvia 100mg, Metformin XR 500mg",
        "notes": (
            "Dr. Rao was very enthusiastic about Januvia. She reviewed the clinical trial "
            "data we shared and said she would start prescribing it for newly diagnosed "
            "Type 2 diabetes patients. Asked for 10 sample packs. Very warm interaction."
        ),
        "summary": (
            "Highly productive visit with Dr. Priya Rao at Apollo Hospital. She expressed "
            "strong interest in Januvia for Type 2 diabetes management after reviewing "
            "clinical data. Committed to prescribing for new patients and requested samples."
        ),
        "sentiment": "positive",
        "follow_up_date": days_from_now(5),
    },
    {
        "hcp_name": "Dr. Karan Malhotra",
        "specialty": "Cardiology",
        "hospital": "Fortis Heart Institute, Delhi",
        "interaction_type": "Meeting",
        "datetime": days_ago(4),
        "products": "Rosuvastatin 10mg, Clopidogrel 75mg",
        "notes": (
            "Excellent meeting. Dr. Malhotra is a key opinion leader in cardiology. "
            "He agreed to include Rosuvastatin in his first-line therapy protocol. "
            "Discussed the JUPITER trial data. He wants to present it at the next "
            "cardiology conference. Invited us to sponsor the event."
        ),
        "summary": (
            "Strategic meeting with KOL Dr. Karan Malhotra at Fortis Heart Institute. "
            "He agreed to adopt Rosuvastatin as first-line therapy and expressed interest "
            "in presenting trial data at an upcoming cardiology conference."
        ),
        "sentiment": "positive",
        "follow_up_date": days_from_now(3),
    },
    {
        "hcp_name": "Dr. Ananya Krishnan",
        "specialty": "Pulmonology",
        "hospital": "Manipal Hospital, Bangalore",
        "interaction_type": "Visit",
        "datetime": days_ago(6),
        "products": "Tiotropium Bromide, Budesonide/Formoterol",
        "notes": (
            "Dr. Krishnan was very receptive. She has been looking for a better COPD "
            "management option. Tiotropium data impressed her. She said she will switch "
            "5 of her current patients to our product this week. Asked for patient "
            "education materials in Kannada."
        ),
        "summary": (
            "Very positive visit with Dr. Ananya Krishnan at Manipal Hospital. She plans "
            "to switch 5 COPD patients to Tiotropium immediately. Requested patient "
            "education materials in regional language."
        ),
        "sentiment": "positive",
        "follow_up_date": days_from_now(7),
    },
    {
        "hcp_name": "Dr. Rajesh Nair",
        "specialty": "Gastroenterology",
        "hospital": "Amrita Institute, Kochi",
        "interaction_type": "Call",
        "datetime": days_ago(1),
        "products": "Pantoprazole 40mg, Domperidone",
        "notes": (
            "Called to follow up on last week's visit. Dr. Nair confirmed he has already "
            "prescribed Pantoprazole to 8 new patients. Very happy with the results. "
            "Asked if we have a combination pack. Wants to meet next week to discuss "
            "the new H. pylori eradication protocol."
        ),
        "summary": (
            "Follow-up call with Dr. Rajesh Nair confirmed 8 new Pantoprazole prescriptions. "
            "HCP is satisfied with outcomes and interested in combination therapy options. "
            "Meeting scheduled to discuss H. pylori protocol."
        ),
        "sentiment": "positive",
        "follow_up_date": days_from_now(6),
    },
    {
        "hcp_name": "Dr. Meera Iyer",
        "specialty": "Rheumatology",
        "hospital": "Christian Medical College, Vellore",
        "interaction_type": "Meeting",
        "datetime": days_ago(3),
        "products": "Methotrexate 15mg, Hydroxychloroquine",
        "notes": (
            "Dr. Iyer is a leading rheumatologist. She was very positive about our "
            "Methotrexate formulation — specifically the reduced GI side effect profile. "
            "She agreed to be a speaker at our upcoming CME event in Chennai. "
            "Will prescribe for RA patients starting next month."
        ),
        "summary": (
            "Excellent meeting with Dr. Meera Iyer at CMC Vellore. She agreed to speak "
            "at our CME event and will begin prescribing our Methotrexate formulation "
            "for rheumatoid arthritis patients next month."
        ),
        "sentiment": "positive",
        "follow_up_date": days_from_now(10),
    },
    {
        "hcp_name": "Dr. Suresh Babu",
        "specialty": "Neurology",
        "hospital": "NIMHANS, Bangalore",
        "interaction_type": "Visit",
        "datetime": days_ago(5),
        "products": "Levetiracetam 500mg, Lamotrigine",
        "notes": (
            "Dr. Babu was very engaged. He reviewed our Levetiracetam data and compared "
            "it favorably with the current standard of care. He mentioned that 30% of "
            "his epilepsy patients are not well-controlled and he wants to try our "
            "product. Requested a clinical presentation for his team next Friday."
        ),
        "summary": (
            "Highly engaged visit with Dr. Suresh Babu at NIMHANS. He identified "
            "approximately 30% of his epilepsy patients as candidates for Levetiracetam "
            "and requested a team clinical presentation."
        ),
        "sentiment": "positive",
        "follow_up_date": days_from_now(2),
    },

    # ── NEGATIVE SENTIMENT (4 records) ───────────────────────────────────────

    {
        "hcp_name": "Dr. Vikram Desai",
        "specialty": "Oncology",
        "hospital": "Tata Memorial Hospital, Mumbai",
        "interaction_type": "Visit",
        "datetime": days_ago(8),
        "products": "Bevacizumab 400mg",
        "notes": (
            "Very difficult visit. Dr. Desai was dismissive from the start. He said he "
            "has had two patients with severe hypertension after Bevacizumab and will "
            "not prescribe it again. He asked us to leave after 5 minutes. Did not "
            "accept any literature. Strongly negative attitude toward our company."
        ),
        "summary": (
            "Challenging visit with Dr. Vikram Desai at Tata Memorial. He reported "
            "adverse events in two patients on Bevacizumab and refused further "
            "engagement. Immediate escalation to medical affairs required."
        ),
        "sentiment": "negative",
        "follow_up_date": days_from_now(21),
    },
    {
        "hcp_name": "Dr. Pooja Agarwal",
        "specialty": "Dermatology",
        "hospital": "AIIMS, New Delhi",
        "interaction_type": "Call",
        "datetime": days_ago(10),
        "products": "Isotretinoin 20mg, Adapalene Gel",
        "notes": (
            "Dr. Agarwal was very unhappy. She said our Isotretinoin pricing is 40% "
            "higher than the competitor and the packaging is inconvenient. She has "
            "switched all her patients to a generic. Said she will not reconsider "
            "unless we offer a significant discount or better patient support program."
        ),
        "summary": (
            "Negative call with Dr. Pooja Agarwal at AIIMS Delhi. She has switched "
            "all patients to generic Isotretinoin due to pricing concerns. Requires "
            "pricing review and patient support program proposal."
        ),
        "sentiment": "negative",
        "follow_up_date": days_from_now(30),
    },
    {
        "hcp_name": "Dr. Harish Reddy",
        "specialty": "Nephrology",
        "hospital": "Yashoda Hospital, Hyderabad",
        "interaction_type": "Meeting",
        "datetime": days_ago(12),
        "products": "Tacrolimus 1mg, Mycophenolate Mofetil",
        "notes": (
            "Meeting went poorly. Dr. Reddy raised serious concerns about the cold "
            "chain management for Tacrolimus. He said two batches arrived at incorrect "
            "temperatures last month. He is considering switching to a competitor. "
            "Escalated to supply chain team. Very frustrated doctor."
        ),
        "summary": (
            "Difficult meeting with Dr. Harish Reddy at Yashoda Hospital. Cold chain "
            "failures for Tacrolimus have damaged trust. Immediate supply chain "
            "investigation and CAPA required to retain this account."
        ),
        "sentiment": "negative",
        "follow_up_date": days_from_now(4),
    },
    {
        "hcp_name": "Dr. Nalini Venkat",
        "specialty": "Psychiatry",
        "hospital": "NIMHANS, Bangalore",
        "interaction_type": "Visit",
        "datetime": days_ago(15),
        "products": "Olanzapine 10mg, Quetiapine",
        "notes": (
            "Dr. Venkat was openly critical. She said our medical representative "
            "previously gave her incorrect dosing information which led to a patient "
            "complaint. She has filed a formal complaint with the hospital pharmacy "
            "committee. Refused to discuss any products. Very serious situation."
        ),
        "summary": (
            "Critical visit with Dr. Nalini Venkat at NIMHANS. A prior misinformation "
            "incident has led to a formal complaint. Requires immediate intervention "
            "from medical affairs and senior management."
        ),
        "sentiment": "negative",
        "follow_up_date": days_from_now(14),
    },

    # ── NEUTRAL SENTIMENT (4 records) ────────────────────────────────────────

    {
        "hcp_name": "Dr. Arjun Mehta",
        "specialty": "Cardiology",
        "hospital": "Fortis Hospital, Delhi",
        "interaction_type": "Call",
        "datetime": days_ago(3),
        "products": "Rosuvastatin 20mg, Clopidogrel 75mg",
        "notes": (
            "Brief call. Dr. Mehta was in between patients. He acknowledged receiving "
            "the product literature we sent. Said he will review it over the weekend. "
            "Not particularly engaged but not negative either. Agreed to a proper "
            "meeting next week."
        ),
        "summary": (
            "Brief call with Dr. Arjun Mehta at Fortis Hospital. He acknowledged "
            "receipt of product literature and agreed to a detailed meeting next week. "
            "Engagement level was neutral."
        ),
        "sentiment": "neutral",
        "follow_up_date": days_from_now(5),
    },
    {
        "hcp_name": "Dr. Sunita Sharma",
        "specialty": "Oncology",
        "hospital": "AIIMS Delhi",
        "interaction_type": "Meeting",
        "datetime": days_ago(1),
        "products": "Pembrolizumab, Nivolumab",
        "notes": (
            "Detailed discussion on immunotherapy. Dr. Sharma is cautious — she wants "
            "more real-world evidence before switching from her current protocol. "
            "Not opposed to our product but needs more data. Asked for the latest "
            "KEYNOTE trial subgroup analysis."
        ),
        "summary": (
            "Informative meeting with Dr. Sunita Sharma at AIIMS Delhi. She is "
            "cautiously interested in immunotherapy options but requires additional "
            "real-world evidence. KEYNOTE subgroup data requested."
        ),
        "sentiment": "neutral",
        "follow_up_date": days_from_now(14),
    },
    {
        "hcp_name": "Dr. Deepak Joshi",
        "specialty": "Orthopedics",
        "hospital": "Kokilaben Hospital, Mumbai",
        "interaction_type": "Visit",
        "datetime": days_ago(7),
        "products": "Diclofenac 75mg SR, Calcium + Vitamin D3",
        "notes": (
            "Standard visit. Dr. Joshi is a regular prescriber of our Diclofenac. "
            "No major concerns. He mentioned that a new competitor has been visiting "
            "him with a similar product at lower price. Did not commit to any change "
            "but seemed open to hearing more about our patient support program."
        ),
        "summary": (
            "Routine visit with Dr. Deepak Joshi at Kokilaben Hospital. He is a "
            "current prescriber but faces competitive pressure. Patient support "
            "program discussion recommended for next visit."
        ),
        "sentiment": "neutral",
        "follow_up_date": days_from_now(8),
    },
    {
        "hcp_name": "Dr. Fatima Sheikh",
        "specialty": "Gynecology",
        "hospital": "Lilavati Hospital, Mumbai",
        "interaction_type": "Call",
        "datetime": days_ago(9),
        "products": "Folic Acid 5mg, Iron Sucrose",
        "notes": (
            "Called to introduce our new Iron Sucrose formulation. Dr. Sheikh listened "
            "politely but said she is currently satisfied with her existing supplier. "
            "She is open to a face-to-face meeting if we can share comparative data. "
            "Not a rejection, just needs more information."
        ),
        "summary": (
            "Introductory call with Dr. Fatima Sheikh at Lilavati Hospital. She is "
            "satisfied with current Iron Sucrose supplier but open to a meeting with "
            "comparative efficacy data."
        ),
        "sentiment": "neutral",
        "follow_up_date": days_from_now(11),
    },
]


def seed():
    create_tables()
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Check existing count
        existing = db.query(Interaction).count()
        print(f"Existing records: {existing}")

        inserted = 0
        for data in SAMPLES:
            # Skip if exact hcp_name + datetime already exists
            exists = (
                db.query(Interaction)
                .filter(
                    Interaction.hcp_name == data["hcp_name"],
                    Interaction.datetime == data["datetime"],
                )
                .first()
            )
            if exists:
                print(f"  SKIP (already exists): {data['hcp_name']}")
                continue

            record = Interaction(**data)
            db.add(record)
            inserted += 1
            print(f"  INSERT: {data['hcp_name']} | {data['sentiment']} | follow-up: {data['follow_up_date'].strftime('%Y-%m-%d')}")

        db.commit()
        print(f"\n✅ Done! Inserted {inserted} new records.")
        print(f"   Total records now: {db.query(Interaction).count()}")

        # Summary
        from sqlalchemy import func
        pos = db.query(func.count(Interaction.id)).filter(Interaction.sentiment == 'positive').scalar()
        neu = db.query(func.count(Interaction.id)).filter(Interaction.sentiment == 'neutral').scalar()
        neg = db.query(func.count(Interaction.id)).filter(Interaction.sentiment == 'negative').scalar()
        upcoming = db.query(func.count(Interaction.id)).filter(
            Interaction.follow_up_date >= datetime.now(timezone.utc)
        ).scalar()

        print(f"\n📊 Dashboard will show:")
        print(f"   ✅ Positive:          {pos}")
        print(f"   ⚪ Neutral:           {neu}")
        print(f"   ❌ Negative:          {neg}")
        print(f"   📅 Upcoming follow-ups: {upcoming}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
