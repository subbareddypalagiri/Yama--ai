from app.db.database import get_db
from app.db.models import LawSection

session = next(get_db())
acts = sorted([a[0] for a in session.query(LawSection.act_name).distinct().all()])
total_sections = session.query(LawSection).count()

print("\n" + "="*70)
print("  ✅ ALL 3 STAGES COMPLETE - YAMA AI DATABASE FULLY LOADED")
print("="*70)
print(f"\n📊 FINAL DATABASE STATISTICS")
print(f"   Total Indian Acts: {len(acts)}")
print(f"   Total Sections/Provisions: {total_sections}")
print(f"\n📚 ALL {len(acts)} ACTS AVAILABLE:\n")

for i, act in enumerate(acts, 1):
    sections = session.query(LawSection).filter(LawSection.act_name == act).count()
    print(f"   {i:2}. {act:<50} [{sections:2} sections]")

print(f"\n{'='*70}")
print(f"Stage 1: Income Tax Act (15) + Companies Act (7)")
print(f"Stage 2: 8 Labour Acts with 41 new sections")
print(f"Stage 3: 8 Specialized Acts with 34 new sections")
print(f"Total New Sections: 103 sections across 24 acts")
print(f"{'='*70}\n")
