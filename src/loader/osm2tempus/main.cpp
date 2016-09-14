#include "pgsql_writer.h"
#include "sqlite_writer.h"

#include <boost/program_options.hpp>

void single_pass_pbf_read( const std::string& filename, Writer& writer );
void two_pass_pbf_read( const std::string& filename, Writer& writer );


int main(int argc, char** argv)
{
    namespace po = boost::program_options;
    using namespace std;

    string db_options = "dbname=tempus_test_db";
    string schema = "_tempus_import";
    string table = "highway";
    string pbf_file = "";

    po::options_description desc( "Allowed options" );
    desc.add_options()
    ( "help", "produce help message" )
    ( "db", po::value<string>(), "set database connection options" )
    ( "schema", po::value<string>(), "set database schema" )
    ( "table", po::value<string>(), "set the table name to populate" )
    ( "pbf", po::value<string>(), "input OSM pbf file" )
    ( "pgis", po::value<string>(), "PostGIS connection options" )
    ( "sqlite", po::value<string>(), "SQLite output file" )
    ( "two-pass", "enable two pass reading" )
    ;

    po::variables_map vm;
    po::store( po::parse_command_line( argc, argv, desc ), vm );
    po::notify( vm );

    if ( vm.count( "help" ) ) {
        std::cout << desc << std::endl;
        return 1;
    }

    if ( vm.count( "db" ) ) {
        db_options = vm["db"].as<string>();
    }
    if ( vm.count( "schema" ) ) {
        schema = vm["schema"].as<string>();
    }
    if ( vm.count( "table" ) ) {
        table = vm["table"].as<string>();
    }
    if ( vm.count( "pbf" ) ) {
        pbf_file = vm["pbf"].as<string>();
    }

    if ( pbf_file.empty() ) {
        std::cerr << "An input PBF file must be specified" << std::endl;
        return 1;
    }

    std::unique_ptr<Writer> writer;
    if ( vm.count( "pgis" ) ) {
        writer.reset( new SQLBinaryCopyWriter( vm["pgis"].as<string>() ) );
    }
    else if ( vm.count( "sqlite" ) ) {
        writer.reset( new SqliteWriter( vm["sqlite"].as<string>() ) );
    }

    if ( vm.count( "two-pass" ) ) {
        two_pass_pbf_read( pbf_file, *writer );
    }
    else
    {
        single_pass_pbf_read( pbf_file, *writer );
    }
    
    return 0;
}
