# Trial Course Conversion & Engagement Analysis

## 🎯 Project Objective
[cite_start]This dashboard analyses a free-to-paid marketing funnel for an online trial course (1,000 users)[cite: 246]. [cite_start]The primary goal is to identify user drop-off points, compare acquisition channel quality, and correlate user engagement (watch time) and feedback (VoC) with final conversion[cite: 247].

## 🛠️ Technical Stack & Workflow
- [cite_start]**Data Engineering (Python & Power Query):** Used Python to generate the raw dataset and Power Query to engineer 'Watch_Bucket' ranges and normalize feedback keywords for accurate counting[cite: 248, 249].
- [cite_start]**Data Modeling:** Built a relational model in Power BI to track 1,000 users across four funnel stages: Watch, Register, Consult, and Paid[cite: 250].
- [cite_start]**Advanced DAX:** Developed measures to calculate conversion rates (e.g., Consult-to-Paid) and a weighted Channel Quality Score[cite: 272, 285].

## 📊 Key Insights
- [cite_start]**Funnel Performance:** The overall conversion rate is 19.8%[cite: 250]. [cite_start]The most significant friction point is the transition from **Consultation to Payment**[cite: 251].
- [cite_start]**Channel Quality:** **WeChat Moments** is the highest-performing channel with a 49% consult-to-paid rate, significantly outperforming Douyin and WeChat Channels[cite: 252, 253].
- [cite_start]**User Engagement:** A strong correlation exists between engagement depth and payment; the paid rate peaks at approximately 42.9% for users in the **15–20 minute watch bucket**[cite: 257].
- [cite_start]**Top Blockers:** Non-paid users primarily cited sales pressure, pricing/value concerns, and content clarity as their main deterrents[cite: 255].

## 🖼️ Dashboard Preview

### Page 1: Funnel Overview
[cite_start]Focuses on overall health and identifying where the largest numeric loss occurs[cite: 270].
![Funnel Overview](screenshots/Page1.png)

### Page 2: Acquisition Analysis
[cite_start]Compares channel traffic volume against conversion quality[cite: 278, 279].
![Acquisition Analysis](screenshots/Page2.png)

### Page 3: Engagement & VoC
[cite_start]Connects "what users do" (watch time) with "what they say" (feedback)[cite: 288].
![Engagement and VoC](screenshots/Page3.png)

### Page 4: Actions & Recommendations
[cite_start]Summarizes findings and provides a high-intent follow-up list for targeted outreach[cite: 302, 308].
![Actions and Recommendations](screenshots/Page4.png)
