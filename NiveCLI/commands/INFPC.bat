@ECHO OFF
:: NOME   :  ScriptNive
:: AUTOR  : Ryan Vinicius Carvalho Pereira
:: VERSAO : Enterprise Release Slim / Básica
REM change CHCP to UTF-8
CHCP 65001
CLS
title ScriptNive 1.6.3
color 9
echo Informações Gerais. 
systeminfo
echo Informações da Processador. 
wmic cpu get name, caption, maxclockspeed, numberofcores, numberoflogicalprocessors
echo Informações da Placa Mãe.
wmic baseboard get manufacturer, product, serialnumber
echo Informações da Placa de vídeo.
wmic path win32_videocontroller get name, caption, adapterram
echo Informações do HD/SSD.
wmic logicaldisk where DeviceID="C:" get size, freespace, filesystem 
echo Informações da memória RAM.
wmic memorychip get capacity & wmic memorychip get speed & wmic memorychip get manufacturer & wmic memorychip get devicelocator & wmic memorychip get partnumber
echo Informações do monitor.
wmic desktopmonitor get Caption, MonitorType, MonitorManufacturer, Name & wmic desktopmonitor get /count
echo Informações de sistema. 
wmic os get caption, version, buildnumber, installDate, lastBootUpTime
echo Informações da Rede.
wmic nic get name, adaptertype, MACAddress, speed
echo Informações da BIOS. 
wmic bios get manufacturer, version, releaseDate, SMBIOSBIOSVersion
pause
exit