#!/bin/bash
. /usr/share/beakerlib/beakerlib.sh || exit 1

rlJournalStart
    rlPhaseStartSetup
        rlRun "pushd data"
    rlPhaseEnd

    for method in ${METHODS:-local}; do
        rlPhaseStartTest "With $method provision method"
            rlRun -s "tmt run -avvvvddd provision -h $method |& tee output.txt"

            rlAssertGrep "out: prepare: stdin: False" output.txt
            rlAssertGrep "out: prepare: stdout: False" output.txt
            rlAssertGrep "out: prepare: stderr: False" output.txt

            rlAssertGrep "out: execute: stdin: False" output.txt
            rlAssertGrep "out: execute: stdout: False" output.txt
            rlAssertGrep "out: execute: stderr: False" output.txt

            rlAssertGrep "out: finish: stdin: False" output.txt
            rlAssertGrep "out: finish: stdout: False" output.txt
            rlAssertGrep "out: finish: stderr: False" output.txt

            rlAssertGrep "out: prepare: stdin: 0" output.txt
            rlAssertGrep "out: prepare: stdout: 0" output.txt
            rlAssertGrep "out: prepare: stderr: 0" output.txt

            rlAssertGrep "out: execute: stdin: 0" output.txt
            rlAssertGrep "out: execute: stdout: 0" output.txt
            rlAssertGrep "out: execute: stderr: 0" output.txt

            rlAssertGrep "out: finish: stdin: 0" output.txt
            rlAssertGrep "out: finish: stdout: 0" output.txt
            rlAssertGrep "out: finish: stderr: 0" output.txt
        rlPhaseEnd

        rlPhaseStartTest "With $method provision method, interactive tests"
            rlRun "../pypty.py 'tmt run -avvvvddd provision -h $method execute -h tmt --interactive' |& tee output.txt"

            rlAssertGrep "out: prepare: stdin: False" output.txt
            rlAssertGrep "out: prepare: stdout: False" output.txt
            rlAssertGrep "out: prepare: stderr: False" output.txt

            rlAssertGrep "execute: stdin: True" output.txt
            rlAssertGrep "execute: stdout: True" output.txt
            rlAssertGrep "execute: stderr: True" output.txt

            rlAssertGrep "out: finish: stdin: False" output.txt
            rlAssertGrep "out: finish: stdout: False" output.txt
            rlAssertGrep "out: finish: stderr: False" output.txt

            rlAssertGrep "out: prepare: stdin: 0" output.txt
            rlAssertGrep "out: prepare: stdout: 0" output.txt
            rlAssertGrep "out: prepare: stderr: 0" output.txt

            rlAssertGrep "execute: stdin: 1" output.txt
            rlAssertGrep "execute: stdout: 1" output.txt
            rlAssertGrep "execute: stderr: 1" output.txt

            rlAssertGrep "out: finish: stdin: 0" output.txt
            rlAssertGrep "out: finish: stdout: 0" output.txt
            rlAssertGrep "out: finish: stderr: 0" output.txt
        rlPhaseEnd
    done

    rlPhaseStartCleanup
        rlRun "popd"
    rlPhaseEnd
rlJournalEnd
