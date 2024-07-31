test:
	sigrok-cli -i test.vcd -P qspi:clk=CLK:mosi=IO0:miso=IO1:io2=IO2:io3=IO3:cs=CS
