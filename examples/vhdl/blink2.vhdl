library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all; -- Unsigned

entity blinky2 is end blinky2;
architecture behaviour of blinky2 is
	signal clk : std_logic := '0';
	signal en0, en1 : std_logic := '0';
	signal sigterm : std_logic := '0';
	signal counter : unsigned(7 downto 0) := x"00";
	signal delayed_counter : unsigned(7 downto 0) := x"00";
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
			if en0 = '1' and en1 = '1' then
				counter <= counter + 1;
			end if;
		end if;
	end process;

	process (delayed_counter)
	begin
		if delayed_counter = 15 then
			sigterm <= '1';
		else
			sigterm <= '0';
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

	delayed_counter(0) <= counter(0) after 10 ns;
	delayed_counter(1) <= counter(1) after 5 ns;
	delayed_counter(2) <= counter(2) after 2 ns;
	delayed_counter(3) <= counter(3) after 6 ns;
	delayed_counter(4) <= counter(4) after 3 ns;
	delayed_counter(5) <= counter(5) after 4 ns;
	delayed_counter(6) <= counter(6) after 7 ns;
	delayed_counter(7) <= counter(7) after 2 ns;

end behaviour;
