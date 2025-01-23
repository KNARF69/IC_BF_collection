-- Author: Frank Kok
-- University of Twente 2024
-- this file contains the BF, but is not the testbench.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use IEEE.NUMERIC_STD.ALL;


use work.all;

entity bfar_hash_V4 is
    port (
	clk   : in std_logic;
    reset : in std_logic;

	injec : in std_logic_vector(63 downto 0);

	busy : out std_logic;		-- 0=idle / 1=busy
	out_bf : out std_logic;		-- 0= miss / 1= hit (thus 1 is positive filter response, either tp or fp)
	out_rdy : out std_logic;	-- 0=not ready / 1=ready
	nxt_inp : in std_logic;		-- 0=busy / 1= ready for next input	//WAS INOUT
	endlist : in std_logic;		-- 0=not end of list / 1=end of list
	outA0, outA1, outA2, outB0, outB1, outB2 : out std_logic := '0'	--output for arrayset
    );
    attribute dont_touch : string;
end entity;

architecture bfarch of bfar_hash_V4 is
	signal din64 : std_logic_vector(63 downto 0) := (others => '0');		--64b hash in
	signal din32 : std_logic_vector(31 downto 0) := (others => '0');		--32b hash in
	signal hen : std_logic := '1';

	signal out_crc32_h0, out_crc32_h1, out_crc32_h2 : std_logic_vector(11 downto 0) := (others => '0');		--32b hash outs
	signal out_crc64_h0, out_crc64_h1, out_crc64_h2 : std_logic_vector(12 downto 0) := (others => '0');		--64b hash outs

	signal ram_addr_A0, ram_addr_A1, ram_addr_A2 : std_logic_vector(9 downto 0) := (others => '0');		--ram addresses
	signal ram_addr_B0, ram_addr_B1, ram_addr_B2 : std_logic_vector(8 downto 0) := (others => '0');

	signal ram_data_in_A0, ram_data_in_A1, ram_data_in_A2 : std_logic_vector(7 downto 0) := (others => '0');	--ram data in
	signal ram_data_in_B0, ram_data_in_B1, ram_data_in_B2 : std_logic_vector(7 downto 0) := (others => '0');

	signal ram_data_out_A0, ram_data_out_A1, ram_data_out_A2 : std_logic_vector(7 downto 0) := (others => '0');	--ram data out
	signal ram_data_out_B0, ram_data_out_B1, ram_data_out_B2 : std_logic_vector(7 downto 0) := (others => '0');

	signal ram_we_A0, ram_we_A1, ram_we_A2, ram_we_B0, ram_we_B1, ram_we_B2 : std_logic := '0';		--ram write enable

	signal fill : std_logic := '0';			--old internal signals
	signal test : std_logic := '1';

	signal errc : std_logic_vector(3 downto 0) := "0000";

	--hashes:
-------------------------------------64b in------------------------
	component crc64_h0
	port ( 
		data_in : in std_logic_vector (63 downto 0);
		crc_en , rst, clk : in std_logic;
		crc_out : out std_logic_vector (12 downto 0)	);
	end component;
	attribute dont_touch of crc64_h0 : component is "yes";

	component crc64_h1
	port ( 
		data_in : in std_logic_vector (63 downto 0);
		crc_en , rst, clk : in std_logic;
		crc_out : out std_logic_vector (12 downto 0)	);
	end component;
	attribute dont_touch of crc64_h1 : component is "yes";

	component crc64_h2
	port ( 
		data_in : in std_logic_vector (63 downto 0);
		crc_en , rst, clk : in std_logic;
		crc_out : out std_logic_vector (12 downto 0)	);
	end component;
	attribute dont_touch of crc64_h2 : component is "yes";

-----------------------------------------32b in----------------------
	component crc32_h0
	port ( 
		data_in : in std_logic_vector (31 downto 0);
		crc_en , rst, clk : in std_logic;
		crc_out : out std_logic_vector (11 downto 0)	);
	end component;
	attribute dont_touch of crc32_h0 : component is "yes";

	component crc32_h1
	port ( 
		data_in : in std_logic_vector (31 downto 0);
		crc_en , rst, clk : in std_logic;
		crc_out : out std_logic_vector (11 downto 0)	);
	end component;
	attribute dont_touch of crc32_h1 : component is "yes";

	component crc32_h2
	port ( 
		data_in : in std_logic_vector (31 downto 0);
		crc_en , rst, clk : in std_logic;
		crc_out : out std_logic_vector (11 downto 0)	);
	end component;
	attribute dont_touch of crc32_h2 : component is "yes";

begin
	--hashes
	h64_0 : crc64_h0
	port map(
		clk => clk,
		rst => reset,
		crc_en => hen,	--hash enable 64 - 0
		data_in => din64,	--hash data in 64 - 0
		crc_out => out_crc64_h0 ); --hash out 64 - 0 == directly tied to port

	h64_1 : crc64_h1
	port map(
		clk => clk,
		rst => reset,
		crc_en => hen,
		data_in => din64,
		crc_out => out_crc64_h1 );

	h64_2 : crc64_h2
	port map(
		clk => clk,
		rst => reset,
		crc_en => hen,
		data_in => din64,
		crc_out => out_crc64_h2 );

	h32_0 : crc32_h0
	port map(
		clk => clk,
		rst => reset,
		crc_en => hen,
		data_in => din32,
		crc_out => out_crc32_h0 );

	h32_1 : crc32_h1
	port map(
		clk => clk,
		rst => reset,
		crc_en => hen,
		data_in => din32,
		crc_out => out_crc32_h1 );

	h32_2 : crc32_h2
	port map(
		clk => clk,
		rst => reset,
		crc_en => hen,
		data_in => din32,
		crc_out => out_crc32_h2 );


--=================================RAMs=================================--
	ram_A0 : entity work.bfar_crc_ram_A0
	port map(
		clk 			=> clk,					--clock
		reset 			=> reset,				--reset
		ram_addr 		=> ram_addr_A0,			--address
		ram_data_in 	=> ram_data_in_A0,		--data in
		ram_data_out	=> ram_data_out_A0,		--data out
		ram_we			=> ram_we_A0	);		--write enable

	ram_A1 : entity work.bfar_crc_ram_A1
	port map(
		clk 			=> clk,					--clock
		reset 			=> reset,				--reset
		ram_addr 		=> ram_addr_A1,			--address
		ram_data_in 	=> ram_data_in_A1,		--data in
		ram_data_out	=> ram_data_out_A1,		--data out
		ram_we			=> ram_we_A1	);		--write enable

	ram_A2 : entity work.bfar_crc_ram_A2
	port map(
		clk 			=> clk,					--clock
		reset 			=> reset,				--reset
		ram_addr 		=> ram_addr_A2,			--address
		ram_data_in 	=> ram_data_in_A2,		--data in
		ram_data_out	=> ram_data_out_A2,		--data out
		ram_we			=> ram_we_A2	);		--write enable

	ram_B0 : entity work.bfar_crc_ram_B0
	port map(
		clk 			=> clk,					--clock
		reset 			=> reset,				--reset
		ram_addr 		=> ram_addr_B0,			--address
		ram_data_in 	=> ram_data_in_B0,		--data in
		ram_data_out	=> ram_data_out_B0,		--data out
		ram_we			=> ram_we_B0	);		--write enable

	ram_B1 : entity work.bfar_crc_ram_B1
	port map(
		clk 			=> clk,					--clock
		reset 			=> reset,				--reset
		ram_addr 		=> ram_addr_B1,			--address
		ram_data_in 	=> ram_data_in_B1,		--data in
		ram_data_out	=> ram_data_out_B1,		--data out
		ram_we			=> ram_we_B1	);		--write enable

	ram_B2 : entity work.bfar_crc_ram_B2
	port map(
		clk 			=> clk,					--clock
		reset 			=> reset,				--reset
		ram_addr 		=> ram_addr_B2,			--address
		ram_data_in 	=> ram_data_in_B2,		--data in
		ram_data_out	=> ram_data_out_B2,		--data out
		ram_we			=> ram_we_B2	);		--write enable
		

--main, contains BF
bf_main: process(clk, reset) is
	
variable input_64 : std_logic_vector(63 downto 0);
variable instr_inp : std_logic_vector(31 downto 0);
variable out640, out641, out642, out320, out321, out322 : std_logic := '0';
variable restA0, restA1, restA2, restB0, restB1, restB2 : integer := 0;
variable memA0, memA1, memA2 : std_logic_vector(9 downto 0);
variable memB0, memB1, memB2 : std_logic_vector(8 downto 0);
variable state : std_logic_vector(1 downto 0) := "00";

begin
if reset = '1' then		--reset

	busy <= '0';
	out_rdy <= '0';
	out_bf <= '0';

	hen <= '1';
	din32 <= (others => '0');
	din64 <= (others => '0');

	input_64 := (others => '0');
	instr_inp := (others => '0');

	out640 := '0';
	out641 := '0';
	out642 := '0';
	out320 := '0';
	out321 := '0';
	out322 := '0';
	restA0 := 0;
	restA1 := 0;
	restA2 := 0;
	restB0 := 0;
	restB1 := 0;
	restB2 := 0;
	memA0 := (others => '0');
	memA1 := (others => '0');
	memA2 := (others => '0');
	memB0 := (others => '0');
	memB1 := (others => '0');
	memB2 := (others => '0');
	state := "00";
	ram_addr_A0 <= (others => '0');
	ram_addr_A1 <= (others => '0');
	ram_addr_A2 <= (others => '0');
	ram_addr_B0 <= (others => '0');
	ram_addr_B1 <= (others => '0');
	ram_addr_B2 <= (others => '0');


elsif rising_edge(clk) and test = '1' then
	if nxt_inp = '1' then					-- first clock cycle of an iteration (1 iteration per input), feed input to hashes
		out_rdy <= '0';
		busy <= '1';
		input_64 := injec;
		instr_inp := injec(31 downto 0);

		din64 <= input_64;
		din32 <= instr_inp;
		state := "01";
		hen <= '1';

		errc <= "0001";

	elsif nxt_inp = '0' and state = "01" then	--second cycle, take output hash and fetch bytes from mem
		--request bytes from mems
		memA0 := out_crc64_h0(12 downto 3);
		memA1 := out_crc64_h1(12 downto 3);
		memA2 := out_crc64_h2(12 downto 3);
		memB0 := out_crc32_h0(11 downto 3);
		memB1 := out_crc32_h1(11 downto 3);
		memB2 := out_crc32_h2(11 downto 3);

		ram_addr_A0 <= memA0;
		ram_addr_A1 <= memA1;
		ram_addr_A2 <= memA2;
		ram_addr_B0 <= memB0;
		ram_addr_B1 <= memB1;
		ram_addr_B2 <= memB2;

		--index for bit in the bytes
		restA0 := to_integer(unsigned(out_crc64_h0(2 downto 0)));
		restA1 := to_integer(unsigned(out_crc64_h1(2 downto 0)));
		restA2 := to_integer(unsigned(out_crc64_h2(2 downto 0)));
		restB0 := to_integer(unsigned(out_crc32_h0(2 downto 0)));
		restB1 := to_integer(unsigned(out_crc32_h1(2 downto 0)));
		restB2 := to_integer(unsigned(out_crc32_h2(2 downto 0)));

		state := "10";
		errc <= "0010";

	elsif nxt_inp = '0' and state = "10" then		--third cycle, extra cycle to wait for mem
		state := "11";
		errc <= "0011";

	elsif nxt_inp = '0' and state = "11" then 		--fourth cycle, check bits, determine filter response (0 or 1). ready for next iteration or endlist
		--bits of interest
		out640 := ram_data_out_A0(restA0);
		out641 := ram_data_out_A1(restA1);
		out642 := ram_data_out_A2(restA2);
		out320 := ram_data_out_B0(restB0);
		out321 := ram_data_out_B1(restB1);
		out322 := ram_data_out_B2(restB2);

		outA0 <= out640;
		outA1 <= out641;
		outA2 <= out642;
		outB0 <= out320;
		outB1 <= out321;
		outB2 <= out322;

		--filter response
		if out640 = '1' and out641 = '1' and out642 = '1' and out320 = '1' and out321 = '1' and out322 = '1' then
			out_bf <= '1';
		else
			out_bf <= '0';
		end if;

		out_rdy <= '1';

		if endlist = '1' then
			busy <= '0';
			errc <= "1100";
		end if;

	end if;
end if;

end process;
end architecture bfarch;