#!/bin/bash

# the directory where the games transcripts are 
DATA=data


COMMENT_CHAR="#"
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color


if [ $# -lt 1 ]; then
	echo "usage: $0 level [prog]"
	exit 1
fi
level=$1
if [ $level -lt 1 ] || [ $level -gt 4 ]; then
	echo "* Only levels [1-4] are defined."
	exit 1
fi

if [ $# -eq 2 ]; then
	CHESS_PROG="$2"
	printf "* Setting ${BLUE}${CHESS_PROG}${NC} passed as a parameter.\n"
else  # No chess executable passed as parameter
	CHESS_PROG="../src/echecs"
	echo "* Using executable ${CHESS_PROG} defined in script."
fi

# test chess binary exists and executable
if ! [ -x "$CHESS_PROG" ]; then
	echo "* Error: $CHESS_PROG is not executable."
	exit 1
fi 


LOG="test.log"
rm -rf $LOG

leg_games=$(ls -1 ${DATA}/${level}-leg-*.txt 2>/dev/null)
ill_games=$(ls -1 ${DATA}/${level}-ill-*.txt 2>/dev/null)
failed_tests=""
for g in $leg_games $ill_games
do
	echo $g | tee -a $LOG
	>&2 echo "* Testing ========== $g " | tee -a $LOG
	grep -v $COMMENT_CHAR $g | "${CHESS_PROG}" >>  $LOG
	retcode=$?
	# grep -v $COMMENT_CHAR $g | (
	#while read ligne
	#do
	#  printf "${BLUE} $ligne ${NC}\n" >> $LOG
      #done) | "${CHESS_PROG}" | tee -a $LOG

	# test: last line of log is expected to be the candidate final 'position<space>res'
	# e.g 
	# wR,wN,,wQ,wK,wB,wN,wR,wP,wP,wP,,wP,wP,wP,wP,,,,,,,,,,,,wP,,,,wB,,,,bP,,bB,,,,,,,,bP,,,bP,bP,bP,,bP,,bP,bP,bR,bN,,bQ,bK,bB,bN,bR, ?-?
      ref_ll=$(tail -1 $g)
	ref_pos=$(echo $ref_ll | cut -f1 -d' ')
	out_ll=$(tail -1 $LOG)
	out_pos=$(echo $out_ll | cut -f1 -d' ')

	# --- test final position
	if [ "$ref_pos" == "$out_pos" ]; then
		  printf "  -> ${GREEN}reference position: OK${NC}\n" | tee -a $LOG
	else
		echo "  -> Final position differs from reference:"
		printf "   ref:[${GREEN}$ref_pos${NC}]\n"  | tee -a $LOG
		printf "   you:[${RED}$out_pos${NC}]\n"    | tee -a $LOG
        msg="${g}_(position)"
		if [ -z "${failed_tests}" ]; then
			failed_tests="$msg"
		else
            failed_tests="${failed_tests} $msg"
		fi
	fi

	# --- test game result
	ref_res=$(echo $ref_ll | cut -f2 -d' ')
	out_res=$(echo $out_ll | cut -f2 -d' ')
	if [ "$ref_res" == "$out_res" ]; then
		  printf "  -> ${GREEN}reference result: OK${NC}\n" | tee -a $LOG
	else
		echo "  -> Game result differs from reference:"
		printf "   ref:[${GREEN}$ref_res${NC}]\n"  | tee -a $LOG
		printf "   you:[${RED}$out_res${NC}]\n"    | tee -a $LOG
        msg="${g}_(result)"
		if [ -z "${failed_tests}" ]; then
			failed_tests="$msg"
		else
            failed_tests="$failed_tests $msg"
		fi
	fi


	# test exit code
	if [ $retcode -ne 0 ]; then
		  printf  " -> ${RED}[test error] (exit code=$retcode) ${NC} $CHESS_PROG ended in error for game $g (around move $retcode)\n" | tee -a $LOG
	else
		  printf "  -> ${NC}(exit code=0)\n" | tee -a $LOG

	fi
done
if [ -n "${failed_tests}" ]; then
	  echo ".----------------------------"
	  echo "| failed tests:              "
      for i in ${failed_tests}; do
          echo "| $i "
      done
	  echo '`----------------------------'
fi
