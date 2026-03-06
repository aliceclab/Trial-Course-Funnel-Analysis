import os
import numpy as np
import pandas as pd



# =========================
# 1) 文件设置
# =========================
# ===== Windows + OneDrive 路径 =====

BASE_DIR = r"C:\Users\alice\OneDrive\Desktop\project 2"

INPUT_FILE = os.path.join(BASE_DIR, "gaotu_freetrial_funnel_v2.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "gaotu_freetrial_funnel_v3.csv")

OVERWRITE_V2_NAME = False

# =========================
# 2) 渠道与转化设定（更真实）
# =========================
# 三个渠道（NZ也能理解）
CHANNELS = [
    "Douyin (TikTok China)",
    "WeChat Moments (朋友圈)",
    "WeChat Channels (视频号)"
]

# 渠道占比：抖音流量最大，朋友圈最小
CHANNEL_PROBS = np.array([0.55, 0.15, 0.30])

# 让“朋友圈质量最高”的转化逻辑（你可以面试讲：熟人信任更强）
# reg_rate: Watch -> Register
# consult_given_reg: Register -> Consult
# paid_given_consult: Consult -> Paid
CHANNEL_RATES = {
    "Douyin (TikTok China)":        {"reg_rate": 0.76, "consult_given_reg": 0.74, "paid_given_consult": 0.28},
    "WeChat Channels (视频号)":      {"reg_rate": 0.79, "consult_given_reg": 0.80, "paid_given_consult": 0.34},
    "WeChat Moments (朋友圈)":       {"reg_rate": 0.83, "consult_given_reg": 0.85, "paid_given_consult": 0.45},
}

# 为了让你 Page1 数字大致稳定（不至于差太多），我们不改变总人数，只改变每个用户的路径


def clamp(value, low, high):
    return max(low, min(high, value))


def generate_feedback_keywords(is_paid: bool, channel: str, rng: np.random.Generator) -> str:
    """
    Paid 用户偏正面；Not Paid 用户偏痛点
    """
    positive_pool = [
        "Content Useful", "Clear Structure", "Good Instructor", "Want More Examples",
        "Practical Tips", "Easy to Follow", "Good Audio"
    ]
    # Not Paid 的常见抱怨（更贴近真实业务）
    negative_pool = [
        "Too Expensive", "Sales Too Pushy", "Not Enough Examples",
        "Audio Bad", "Instructor Boring", "Pace Too Fast", "Hard to Follow",
        "Need More Support", "Content Too Basic"
    ]

    if is_paid:
        choices = rng.choice(positive_pool, size=rng.integers(1, 3), replace=False)
    else:
        # 让不同渠道抱怨略有差异（抖音更容易觉得“太贵/被销售催”，朋友圈更容易觉得“想要更多支持/案例”）
        weights = np.ones(len(negative_pool), dtype=float)
        if channel == "Douyin (TikTok China)":
            for k in ["Too Expensive", "Sales Too Pushy"]:
                weights[negative_pool.index(k)] *= 1.8
        elif channel == "WeChat Moments (朋友圈)":
            for k in ["Need More Support", "Not Enough Examples"]:
                weights[negative_pool.index(k)] *= 1.6
        else:  # Channels
            for k in ["Pace Too Fast", "Hard to Follow"]:
                weights[negative_pool.index(k)] *= 1.4

        weights = weights / weights.sum()
        # 选 1~3 个关键词
        size = rng.integers(1, 4)
        choices = rng.choice(negative_pool, size=size, replace=False, p=weights)

    return ", ".join(choices)


def generate_dropoff_point(completion_rate: float, rng: np.random.Generator) -> str:
    """
    完播率越低越可能在 Intro/Middle 掉；越高越可能 End 或 Sales_Pitch
    """
    if completion_rate < 0.35:
        return rng.choice(["Intro", "Middle"], p=[0.7, 0.3])
    elif completion_rate < 0.70:
        return rng.choice(["Middle", "Sales_Pitch"], p=[0.65, 0.35])
    else:
        return rng.choice(["Sales_Pitch", "End"], p=[0.35, 0.65])


def main():
    rng = np.random.default_rng(20260108)

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"找不到输入文件：{INPUT_FILE}\n"
            "请确认 gaotu_freetrial_funnel_v2.csv 在 Desktop，或修改脚本里的 INPUT_FILE 文件名。"
        )

    df = pd.read_csv(INPUT_FILE)

    # =========================
    # 3) 生成 3 个渠道
    # =========================
    n = len(df)
    new_channels = rng.choice(CHANNELS, size=n, p=CHANNEL_PROBS)
    df["Source_Channel"] = new_channels

    # =========================
    # 4) 按渠道重新生成漏斗路径（更真实：Paid 不再几乎等于 Consult）
    # =========================
    registration_status_list = []
    consultation_booked_list = []
    enrollment_status_list = []

    completion_rate_list = []
    watch_minutes_list = []
    speed_watch_list = []
    dropoff_list = []
    lead_score_list = []
    nps_list = []
    feedback_list = []

    # 假设你的免费先行课时长大约 20 分钟（你可以改）
    total_video_minutes = 20.0

    for i in range(n):
        channel = df.loc[i, "Source_Channel"]
        rates = CHANNEL_RATES[channel]

        # 1) Register
        is_registered = rng.random() < rates["reg_rate"]
        registration_status = "Registered" if is_registered else "Visitor"

        # 2) Consult（只能在 Registered 基础上发生）
        if is_registered:
            is_consult = rng.random() < rates["consult_given_reg"]
        else:
            is_consult = False

        consultation_booked = "Yes" if is_consult else "No"

        # 3) Paid（只能在 Consult 基础上发生）
        if is_consult:
            is_paid = rng.random() < rates["paid_given_consult"]
        else:
            is_paid = False

        enrollment_status = "Paid" if is_paid else "Not Paid"

        # =========================
        # 5) 行为数据（让渠道差异更像真实）
        # =========================
        # completion: 朋友圈更认真，抖音更冲动
        base_mu = {
            "Douyin (TikTok China)": 0.62,
            "WeChat Channels (视频号)": 0.68,
            "WeChat Moments (朋友圈)": 0.75,
        }[channel]

        # 已付费/已咨询的人通常更投入（完播更高）
        if is_paid:
            mu = base_mu + 0.12
        elif is_consult:
            mu = base_mu + 0.06
        elif is_registered:
            mu = base_mu + 0.02
        else:
            mu = base_mu - 0.10

        mu = clamp(mu, 0.05, 0.95)

        # 用 Beta 分布生成 0~1 完播率
        alpha = 6 * mu
        beta = 6 * (1 - mu)
        completion_rate = float(rng.beta(alpha, beta))
        completion_rate = clamp(completion_rate, 0.02, 0.99)

        # watch minutes
        watch_minutes = completion_rate * total_video_minutes

        # speed watching：抖音更容易倍速，朋友圈更少
        speed_prob = {
            "Douyin (TikTok China)": 0.45,
            "WeChat Channels (视频号)": 0.35,
            "WeChat Moments (朋友圈)": 0.25,
        }[channel]
        is_speed = rng.random() < speed_prob
        speed_watch = "Yes" if is_speed else "No"

        # drop-off point
        dropoff_point = generate_dropoff_point(completion_rate, rng)

        # lead score：结合完播 + 是否注册/咨询/付费 + 倍速略扣分
        lead_score = 30 + 55 * completion_rate
        if is_registered:
            lead_score += 8
        if is_consult:
            lead_score += 12
        if is_paid:
            lead_score += 10
        if is_speed:
            lead_score -= 4

        lead_score = int(clamp(round(lead_score), 0, 100))

        # NPS：Paid 更高；Not Paid 更低（但不全是1分）
        if is_paid:
            nps = int(clamp(round(rng.normal(9.0, 1.0)), 1, 10))
        else:
            nps = int(clamp(round(rng.normal(6.0, 2.0)), 1, 10))

        feedback_keywords = generate_feedback_keywords(is_paid, channel, rng)

        # 写回列表
        registration_status_list.append(registration_status)
        consultation_booked_list.append(consultation_booked)
        enrollment_status_list.append(enrollment_status)

        completion_rate_list.append(round(completion_rate, 2))
        watch_minutes_list.append(round(watch_minutes, 1))
        speed_watch_list.append(speed_watch)
        dropoff_list.append(dropoff_point)
        lead_score_list.append(lead_score)
        nps_list.append(nps)
        feedback_list.append(feedback_keywords)

    df["Registration_Status"] = registration_status_list
    df["Consultation_Booked"] = consultation_booked_list
    df["Enrollment_Status"] = enrollment_status_list

    df["Video_Completion_Rate"] = completion_rate_list
    df["Watch_Duration_Mins"] = watch_minutes_list
    df["Is_Speed_Watching"] = speed_watch_list
    df["Drop_off_Point"] = dropoff_list

    df["Lead_Score"] = lead_score_list
    df["NPS_Score"] = nps_list
    df["Feedback_Keywords"] = feedback_list

    # =========================
    # 6) 保存
    # =========================
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Saved: {os.path.basename(OUTPUT_FILE)}")

    # 简单汇总：整体漏斗
    total_users = df["User_ID"].nunique() if "User_ID" in df.columns else len(df)
    reg_users = df.loc[df["Registration_Status"] == "Registered", "User_ID"].nunique() if "User_ID" in df.columns else (df["Registration_Status"] == "Registered").sum()
    consult_users = df.loc[df["Consultation_Booked"] == "Yes", "User_ID"].nunique() if "User_ID" in df.columns else (df["Consultation_Booked"] == "Yes").sum()
    paid_users = df.loc[df["Enrollment_Status"] == "Paid", "User_ID"].nunique() if "User_ID" in df.columns else (df["Enrollment_Status"] == "Paid").sum()

    print(f"Watch: {total_users}")
    print(f"Register: {reg_users} ({reg_users/total_users:.1%})")
    print(f"Consult: {consult_users} ({consult_users/total_users:.1%}) | Consult/Reg: {consult_users/max(reg_users,1):.1%}")
    print(f"Paid: {paid_users} ({paid_users/total_users:.1%}) | Paid/Consult: {paid_users/max(consult_users,1):.1%}")

    # 如果你想覆盖 v2 文件名（让 Power BI Refresh 自动更新）
    if OVERWRITE_V2_NAME:
        overwrite_path = INPUT_FILE
        df.to_csv(overwrite_path, index=False)
        print(f"⚠️ Also overwritten: {os.path.basename(overwrite_path)} (for Power BI refresh)")


if __name__ == "__main__":
    main()
