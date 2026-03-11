import matplotlib.pyplot as plt


def age_distribution(df):

    plt.figure()

    plt.hist(df["age"], bins=30)

    plt.title("Age Distribution of Patients")

    plt.xlabel("Age")

    plt.ylabel("Frequency")

    plt.savefig("../visualizations/healthcare/age_distribution.png")

    plt.close()


def disease_distribution(df):

    disease = df["stroke"].value_counts()

    plt.figure()

    disease.plot(kind="bar")

    plt.title("Stroke Cases Distribution")

    plt.xlabel("Stroke")

    plt.ylabel("Count")

    plt.savefig("../visualizations/healthcare/stroke_distribution.png")

    plt.close()


def bmi_vs_age(df):

    plt.figure()

    plt.scatter(df["age"], df["bmi"])

    plt.title("Age vs BMI")

    plt.xlabel("Age")

    plt.ylabel("BMI")

    plt.savefig("../visualizations/healthcare/age_vs_bmi.png")

    plt.close()


def glucose_distribution(df):

    plt.figure()

    plt.hist(df["avg_glucose_level"], bins=30)

    plt.title("Glucose Level Distribution")

    plt.xlabel("Glucose Level")

    plt.ylabel("Frequency")

    plt.savefig("../visualizations/healthcare/glucose_distribution.png")

    plt.close()