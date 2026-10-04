# Guided localhost test script (test_pack/)
Run: streamlit run ui.py   then follow in order. EXPECTED = pass.

1. Select GP-1001 -> Assemble.
   EXPECT: Shariah 100/100, Citations KPI = 7, gaps = 2.
2. Sidebar upload: ext_news_tobacco.md as EXTERNAL.
   EXPECT: auto re-assemble; Shariah score drops to 60; R3 flag 'tobacco';
   SCU review queue shows 1 item; appendix gains an external row for this file.
3. Upload int_board_resolution.md as INTERNAL.
   EXPECT: appendix gains internal row; memo section 5 cites it.
   NOTE: gaps table unchanged on purpose - KYC status is a system-of-record
   field; in the pilot it syncs from the bank's checklist API.
4. Switch to NS-1002 -> upload ext_bureau_novasteel.csv as EXTERNAL.
   EXPECT: CSV parsed; appendix excerpt shows 'metric | value | as_of';
   Risk section cites bureau rows (overdue instances, bounced cheques).
5. Switch to HM-1003 -> upload int_meeting_notes_hilal.txt as INTERNAL.
   EXPECT: 'utilisation 55%' and '150 days' appear in cited memo text.
6. Approve & Export: tick RM + Credit + SCU -> Download.
   EXPECT: filename hash differs from previous download; audit trail shows
   upload / assemble / approve / export_version events with chained hashes.
7. Sidebar -> Remove uploaded sources (back on GP-1001).
   EXPECT: score returns to 100; appendix back to 7 citations.

Demo-Day stunt: do step 2 LIVE on stage - drop a news PDF on an open client
and watch the Shariah score move in front of the judges.
