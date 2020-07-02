library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all; -- Unsigned

entity blinky is end blinky;
architecture behaviour of blinky is
	signal clk : std_logic := '0';
	signal en0, en1 : std_logic := '0';
	signal sigterm : std_logic := '0';
	signal counter : unsigned(7 downto 0) := x"00";
begin

masterclock:
	process
	begin
		wait for 5 us;
		clkloop : loop
			wait for 1 us;
			clk <= not clk;
			if sigterm = '1' then
				exit;
			end if;
		end loop clkloop;
		wait for 5 us;
		wait;
	end process;

uut:
	process (clk)
	begin
		if rising_edge(clk) then
			if counter = 15 then
				sigterm <= '1';
			end if;
			if en0 = '1' and en1 = '1' then
				counter <= counter + 2;
			end if;
		end if;
	end process;

stimulus:
	process
	begin
		wait for 6 us;
		en0 <= '1';
		wait for 7 us;
		en0 <= '0';
		en1 <= '1';
		wait for 7 us;
		en0 <= '1';
		wait;
	end process;
end behaviour;
