echo: make an installer?
pause

call make_talos_wps.bat a
call make_talos_wheels.bat a
call make_pip_wheels.bat a

@echo done!

pause