import os
import matplotlib.pyplot as plt
import pandas as pd

# Create output folder automatically
OUTPUT_DIR = "../visualizations/students"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def pass_fail_chart(df):
    plt.figure()
    df["pass_status"].value_counts().plot(kind="bar")
    plt.title("Pass vs Fail Distribution")
    plt.xlabel("Status")
    plt.ylabel("Number of Students")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "pass_fail_distribution.png"))
    plt.close()


def subject_performance(df):
    plt.figure()
    df[["math_score", "science_score", "english_score"]].mean().plot(kind="bar")
    plt.title("Average Subject Scores")
    plt.ylabel("Average Score")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "average_subject_scores.png"))
    plt.close()


def attendance_correlation(df):
    correlation = df["attendance_percentage"].corr(df["average_score"])

    plt.figure()
    plt.scatter(df["attendance_percentage"], df["average_score"])
    plt.title(f"Attendance vs Average Score (Corr={correlation:.2f})")
    plt.xlabel("Attendance Percentage")
    plt.ylabel("Average Score")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "attendance_vs_average_score.png"))
    plt.close()

    print("Correlation:", correlation)