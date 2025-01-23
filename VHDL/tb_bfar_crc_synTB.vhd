-- Author: Frank Kok
-- Base of the tb generated online at https://vhdl.lapinoo.net on 12.9.2024 12:32:43 UTC
-- University of Twente 2024

library ieee;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_bfar_synTB is
    port (
    clk     : in std_logic;
    reset   : in std_logic;
    out_bf_res  : out std_logic;
    missled : out std_logic;
    indicled : out std_logic;
    finitoled : out std_logic;
    button  : in std_logic
    );
end tb_bfar_synTB;

architecture tb of tb_bfar_synTB is

    component bfar_hash_V4
        port (clk     : in std_logic;
              reset   : in std_logic;
              injec   : in std_logic_vector (63 downto 0);
              busy    : out std_logic;
            --   test    : out std_logic;
              out_bf  : out std_logic;
              out_rdy : out std_logic;
              nxt_inp : in std_logic;
              endlist : in std_logic;
              outA0   : out std_logic;
              outA1   : out std_logic;
              outA2   : out std_logic;
              outB0   : out std_logic;
              outB1   : out std_logic;
              outB2   : out std_logic);
    end component;

    -- signal clk     : std_logic;
    -- signal reset   : std_logic;
    signal injec   : std_logic_vector (63 downto 0) := (others => '0');
    signal busy    : std_logic;
    -- signal test    : std_logic;
    signal out_bf  : std_logic;
    signal out_rdy : std_logic;
    signal nxt_inp : std_logic := '0';
    signal endlist : std_logic := '0';
    signal outA0   : std_logic;
    signal outA1   : std_logic;
    signal outA2   : std_logic;
    signal outB0   : std_logic;
    signal outB1   : std_logic;
    signal outB2   : std_logic;

    -- signal idleled : std_logic := '1';

    signal ram_addr_inj : std_logic_vector(6 downto 0) := (others => '0');
    signal ram_data_in_inj : std_logic_vector(63 downto 0) := (others => '0');
    signal ram_data_out_inj : std_logic_vector(63 downto 0);
    signal ram_we_inj : std_logic := '0';

    signal hitcounter : integer := 0;
    signal misscounter : integer := 0;
    signal A0hitcnt : integer := 0;
    signal A1hitcnt : integer := 0;
    signal A2hitcnt : integer := 0;
    signal B0hitcnt : integer := 0;
    signal B1hitcnt : integer := 0;
    signal B2hitcnt : integer := 0;

    signal next_instr : std_logic_vector(63 downto 0) := (others => '0');
    signal init : std_logic := '0';
    signal addr_cntr : integer := 0;
    signal state : std_logic_vector(1 downto 0) := "00";
    signal waspressed : std_logic := '0';
    signal done : std_logic := '0';

    type tb_state_type is (initil, fetch_addr, waitfor, result, finito);
    signal tb_state : tb_state_type := initil;
    

    -- constant TbPeriod : time := 1000 ns; -- EDIT Put right period here
    -- signal TbClock : std_logic := '0';
    -- signal TbSimEnded : std_logic := '0';

begin

    dut : bfar_hash_V4
    port map (clk     => clk,
              reset   => reset,
              injec   => injec,
              busy    => busy,
            --   test    => test,
              out_bf  => out_bf,
              out_rdy => out_rdy,
              nxt_inp => nxt_inp,
              endlist => endlist,
              outA0   => outA0,
              outA1   => outA1,
              outA2   => outA2,
              outB0   => outB0,
              outB1   => outB1,
              outB2   => outB2);


    inj_ram : entity work.bfar_TBmem_inj1
    port map(
        clk 			=> clk,					--clock
        reset 			=> reset,				--reset
        ram_addr 		=> ram_addr_inj,			--address
        ram_data_in 	=> ram_data_in_inj,		--data in
        ram_data_out	=> ram_data_out_inj,		--data out
        ram_we			=> ram_we_inj	);		--write enable

tb_main : process(clk, reset)
begin

    if reset = '1' then
        injec <= (others => '0');
        nxt_inp <= '0';
        endlist <= '0';
        init <= '0';
        addr_cntr <= 0;
        state <= "00";
        ram_addr_inj <= (others => '0');
        next_instr <= ram_data_out_inj;
        waspressed <= '0';

        done <= '0';
        hitcounter <= 0;
        misscounter <= 0;
        A0hitcnt <= 0;
        A1hitcnt <= 0;
        A2hitcnt <= 0;
        B0hitcnt <= 0;
        B1hitcnt <= 0;
        B2hitcnt <= 0;

        tb_state <= initil;

        out_bf_res <= '0';
        missled <= '0';
        indicled <= '0';
        finitoled <= '0';



    elsif rising_edge(clk) then

        case tb_state is
            when initil =>				--button pressed, start iteration tb, give next instr to BF
                init <= '1';
                next_instr <= ram_data_out_inj;
                if button = '1' then
                    tb_state <= fetch_addr;
                    waspressed <= '1';
                end if;

            when fetch_addr =>			--fetch instr for next iteration
                injec <= next_instr;
                nxt_inp <= '1';
                ram_addr_inj <= std_logic_vector(to_unsigned(addr_cntr, ram_addr_inj'length));
                if addr_cntr >= 128 then
                    endlist <= '1';
                end if;

                if addr_cntr mod 2 = 0 then
                    indicled <= '1';
                else
                    indicled <= '0';
                end if;

                finitoled <= '0';
                addr_cntr <= addr_cntr + 1;
                tb_state <= waitfor;

            when waitfor =>		--wait
                nxt_inp <= '0';
                if button = '0' then
                    waspressed <= '0';
                end if;

                if waspressed = '0' then
                    tb_state <= result;
                end if;

            when result =>		--retrieve result from BF, log data
                if out_rdy = '1' then
                    next_instr <= ram_data_out_inj;


                    if out_bf = '1' then
                        out_bf_res <= '1';
                        hitcounter <= hitcounter + 1;
                        missled <= '0';
                    else
                        misscounter <= misscounter + 1;
                        out_bf_res <= '0';
                        missled <= '1';
                    end if;

                    if outA0 = '1' then
                        A0hitcnt <= A0hitcnt + 1;
                    end if;
                    if outA1 = '1' then
                        A1hitcnt <= A1hitcnt + 1;
                    end if;
                    if outA2 = '1' then
                        A2hitcnt <= A2hitcnt + 1;
                    end if;
                    if outB0 = '1' then
                        B0hitcnt <= B0hitcnt + 1;
                    end if;
                    if outB1 = '1' then
                        B1hitcnt <= B1hitcnt + 1;
                    end if;
                    if outB2 = '1' then
                        B2hitcnt <= B2hitcnt + 1;
                    end if;

                    if endlist = '1' then
                        done <= '1';
                        tb_state <= finito;
                    else
                        tb_state <= initil;
                    end if;
                end if;

            when finito =>		--finished the list of inputs.
                finitoled <= '1';

        end case;

    end if;

    
end process;

end tb;

