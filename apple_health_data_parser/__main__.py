from apple_health_data_parser.parser import HealthDataParser
import click 

@click.command()

def main():
    file = "../my_life_analytics/data/apple_health_export/Export.xml"
    df = HealthDataParser().parse(file)
    print(df)
    print(df.dtypes)

if __name__ == "__main__":
    main()