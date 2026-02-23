import csv

def export_results(output_list, user_info, timestamp):
    base = f"SRFD_Report_{timestamp}"
    csv_filename = base + ".csv"

    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Champ", "Valeur"])

        # Infos utilisateur
        for key, val in user_info.items():
            writer.writerow([key, val])

        writer.writerow([])

        # Résultats
        writer.writerow(["Résultats", ""])
        for key, val in output_list.items():
            writer.writerow([key, val])

    return csv_filename
