import csv


def export_regions_csv(regions, path):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Region ID", "Area", "Width", "Height", "Centroid X", "Centroid Y", "Relative Area %"])
        for r in regions:
            writer.writerow([r["region_id"], r["area"], r["width"], r["height"],
                              r["centroid"][0], r["centroid"][1], r["relative_area"]])
    return path
