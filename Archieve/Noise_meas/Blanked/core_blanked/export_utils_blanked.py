import csv

def export_results(output_list, user_info, timestamp):
    base = f"LNA_Report_{timestamp}"

    csv_filename = base + ".csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Champ", "Valeur"])
        for key, val in user_info.items():
            writer.writerow([key, val])

        writer.writerow([])
        writer.writerow(["Résultats LNA", ""])
        for line in output_list:
            writer.writerow([line, ""])

    return csv_filename
