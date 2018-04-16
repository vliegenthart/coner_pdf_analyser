#/bin/bash

# BEFORE RUNNING THIS SCRIPT, MAKE SURE ALL PDF FILES AND PDF_NAME_entities.json ARE THERE!
# Retrain PDFNLT so all training CSV's are there!

# TODO
# Do XHTML enrichtment after calculating top papers, not before!
# Change all 'ocurrances' to 'occurrences'
# Balance papers that are used equally from all 10 journals before taking top!!!
# NOTE: Have to manually change pdf loading directory to match database
# Make PDFNLT pdfanalyzer/pdf directory database dependent and ALL scripts calling that directory
# Also add a normalizaion step to calculation top papers #occurrences for method AND dataset: Normalize on number pages, so get density of occs per page


# ############## #
#      SETUP     #
# ############## #

script=$(cd $(dirname $0) && pwd)

# <pdf_dir>: ../PDFNLT/pdfanalyzer/pdf/

usage() {
  echo -e "Usage: $0 [-f] <database> <pdf_dir>"
}

unset force

while getopts "fo:vi" o; do
  case "${o}" in
    f)
      force=1
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done
shift $((OPTIND-1))

if [[ -z "$1" ]] || [[ -z "$2" ]]
then
  usage
  exit 1
fi

echo $2
xhtmls=()
shopt -s nullglob


if [ -f "$2" ]
then
  # Individual files
  dir=$(cd $(dirname "$2")/.. && pwd)
  files=("$2")
else
  # Whole directory, non-forced
  dir="$(cd $(dirname "$2") && pwd)"
  files=("$dir"/pdf/*.pdf)
fi
outdir="${outdir:-$dir/text}"

pdfs=()

tsvs=()

for i in "${files[@]}"
do
  # If not forced, then only pick the files that are not up-to-date
  file="$(basename "$i" .xhtml)"
  file="${file%.pdf}"
  if [ -f "$dir/pdf/$file.pdf" -o -n "$force" ]
  then
    pdfs+=("$dir/pdf/$file.pdf")
    tsvs+=("$file.csv")
    xhtmls+=("$dir/xhtml/$file.xhtml")
  fi
done

if [ ${#pdfs[@]} -eq 0 ]
then
  # Everything is up-to-date, nothing to do
  echo "No papers to analyse!"
  exit
fi

# ##################### #
#      DEPENDENCIES     #
# ##################### #

echo "---------------------------------"
echo "-     CHECKING DEPENDENCIES     -"
echo "---------------------------------"
# echo '✓'
# echo '×' 

if [ -d "$script/../PDFNLT/" ]; then
  echo "✓ PDFNLT"
else
  echo -e "× PDFNLT required in parent directory"
  exit -1
fi

if [ -e "$script/$2" ]; then
  echo "✓ PDF file found"
else
  echo -e "PDF file not found"
  exit -1
fi

# Load RVM into a shell session *as a function*
# Loading RVM *as a function* is mandatory
# so that we can use 'rvm use <specific version>'
if [[ -s "$HOME/.rvm/scripts/rvm" ]] ; then
  # First try to load from a user install
  source "$HOME/.rvm/scripts/rvm"
  echo "✓ RVM user install found: $HOME/.rvm/scripts/rvm"
elif [[ -s "/usr/local/rvm/scripts/rvm" ]] ; then
  # Then try to load from a root install
  source "/usr/local/rvm/scripts/rvm"
  echo "✓ RVM root install found: /usr/local/rvm/scripts/rvm"
else
  echo -e "RVM installation was not found"
  exit -1
fi

echo ""

database=$1
pdf_dir=$2

echo "Variables:"
echo "DATABASE: $database"
echo "PDF_DIR: $pdf_dir"

# ##################### #
#      PROCESS PDFS     #
# ##################### #

echo "--------------------------------------"
echo "-     RUNNING PDFNLT POSTPROCESS     -"
echo "--------------------------------------"

# Copy pdf to PDFNLT and NER
# echo "Copying PDF files from PDFNLT to NER and data/pdf/..."

# Remove xhtml file from PDFNLT/xhtml
# rm -Rf "../PDFNLT/pdfanalyzer/xhtml/$pdf_name.xhtml"

# ###################### #
#      PROCESS TERMS     #
# ###################### #

echo "Creating/updating training files for PDFs..."

for i in "${pdfs[@]}"
do
  pdf_name="$(basename "$i" .pdf)"
  touch -a "../PDFNLT/pdfanalyzer/train/$pdf_name.csv"
done

echo "Running PDFNLT postprocessing for $pdf_dir..."

# To DEBUG: bash -x prints all statements executed
# bash -x "$script/../PDFNLT/postprocess/postprocess.sh" "$pdf_dir"

rvm use jruby-9.1.13.0@pdfnlt
if [ -n "$force" ]
then
  # NOTE: Have to manually change pdf loading directory to match database
  sh "../PDFNLT/postprocess/postprocess.sh" "-f" "$pdf_dir"
else
  sh "../PDFNLT/postprocess/postprocess.sh" "$pdf_dir"
fi

# TO DEBUG RUN SINGLE PAPER FOR NEXT EXECUTION
# rm "../PDFNLT/pdfanalyzer/train/TUD-LTE.csv"










