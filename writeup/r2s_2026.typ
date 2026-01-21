#set text(size: 1.2em)
#set math.equation(numbering: "1")

== Academic value

Through this project we aim to advance the understanding of hybrid rocket motors in a number of key ways. A main objective is to democratize space flight by making engine designs that can be produced as cheaply as possible, e.g. through the use of as many cots components as possible. Further we aim to improve the theoretical understanding of motors by extending the modeling tools available. As such we have extended Rick Newlands NitrousEngineSim by creating a python api for it and adding tooling for adding arbitrary chemistry via propep 3 and adding hybrid paraffin chemistry specifically. We are working together with Rick to make this enhanced version of the software available. Lastly we are focusing on ignition, as this has proven as a particularly challenging practical issue in hybrid engine development, we hope to be able to share our findings after the competition on this topic.

== Aim

Our goal for this year is to build a simple hybrid engine that would allow us to go for a space shot. As the definition for space we will be using the Karman line, which is at 100km. 

== Vehicle

To estimate the dimensions and the performance characteristics of a rocket that we could reach space with we are taking our current construction methods for building rockets. This design utilizes of the shelf carbon fibre tubing and custom machined aluminum coupling rings to allow a modular design of the rocket. As these sections are of known weight per length and per added module this allows us to estimate what a space shot rocket would weigh. We are also confident to be able to mount the engine tank and any plumbing in the current design without adding significant weight 


#figure(
    table(
        columns: 4,
        rows: 8,
        [Part],                 [Mass], [Count], [Mass total],
        [Fin section],          [1kg],  [1],     [1kg],
        [Main parachute bay],   [1kg],  [1],     [1kg],
        [Drogue parachute bay], [0.5kg],[1],     [0.5kg],
        [Nose cone],            [0.5kg],[1],     [1kg],
        [Avionics],             [1kg],  [1],     [1kg],
        [Tank section outer shell], [1.5kg], [1],  [1.5kg],
        [Coupling rings],       [0.15kg],  [5],  [0.75kg],
        [Nitrous tank (dry)], [?], [1], [?],
        [Plumbing ], [?], [1], [?],
        [Engine (dry)], [?], [1], [?],
    ),
    caption: [Proposed Aberdeen space shot rocket mass]
)<mass_overview>

@mass_overview shows an overview of each module of the rocket and what we expect it to weigh. It can be seen that we expect the entire launch vehicle to come in at around 6.75kg, excluding the nitrous tank, engine and plumbing. Making a pessimistic guess that these systems would come in at 18.25kg, resulting in a total dry mass of the launch vehicle of 25kg. Any additional mass savings would then go towards a potential payload.\
\
Based on engine sizing, detailed in Part A, we'll be going with a diameter of 160mm of the launch vehicle.

== Flight simulation

To estimate the altitude reached by such a vehicle we have written a simple python simulation. It assumes the following equation to calculate the acceleration of the rocket:

$ a(t) = g + (F_t (t) + F_d (t))/(m (t)) $<gov_eq>

where $g$ is acceleration due to gravity, $F_t$ the thrust produced by the engine, $F_d$ the drag force and $m$ the current mass of the rocket.\
The mass is made up of a dry mass component and the fuel/ox mass: 
$m(t) = m_d + m_f (t)$. 
Thrust is defined as:
$ F_t = cases(0 &"if" m_f &<= 0, F_("design") &"if" m_f &> 0) $

Finally the drag is given by:
$   
  F_d = 1/2 * rho_("air")(h) * C_(d)(M) * A * v(t)^2
$

with $rho_("air")$ being the density of the atmosphere, $C_(d)(M)$ the coefficient of drag at a given mach number $M$, $A$ the cross sectional area of the rocket ($A = pi r^2$) and $v(t)$ the velocity of the rocket. The mach number $M$ being defined as $M = v/c$ where c is the speed of sound itself defined as $sqrt(gamma_("air")*R_("air")*T_("air"))$, using the well known thermodynamic properties of air and its temperature (more on this further below). As the current acceleration of the rocket is itself dependent on the velocity @gov_eq becomes a differential equation, which we solve computationally using the euler method.\

#figure(
    image("../output/r2s_2026/cira_density.png"),
    caption: [
        Air density at different altitudes from the CIRA-86
        dataset
        ]
)<fig:cira_density>

To model the atmosphere's pressure and temperature, and therefore density we are using the 
COSPAR International Reference Atmosphere (CIRA-86) @NASA_National_Space_Science_Data_Center_2007 at a latitude of 67 (Aberdeen) at an annual mean. A plot of this density) at different altitude can be seen in @fig:cira_density.

#figure(
    image("../output/r2s_2026/mjollnir_drag.png"),
    caption: [Drag of the Mjoellnir rocket at different Mach numbers]
)<mjollnir_drag>

To calculate the drag of the rocket we are using data obtained by M. S. d. Filippi @FILIPPI. The drag obtained for the Mjoellnir launch vehicle presented in that study can be found in @mjollnir_drag. The vehicle should be similar enough to our eventual vehicle to offer a suitable approximation. We applied an additional factor $C_("d, Aberdeen space shot") = 1.2 * C_("d, Mjollnir") $, to account for potential worse then expected air resistance of our vehicle.

Given our propellant choice of paraffin + nitrous oxide and a chamber pressure of 50bar the maximum specific impulse that could theoretically be achieved is around $I_"sp" = 250s$. Accounting for combustion inefficiencies and nozzle imperfections we'll assume a value of $I_"sp" = 230s$.

Based on these numbers a propellant weight of $25"kg"$ results in an altitude reached of $115k m$. The simulated flight profile of the flight can be seen in @fig:flight_sim.

#figure(
    image("../output/r2s_2026/r2s_paraffin.png"),
    caption: [Simple flight simulation for the proposed Aberdeen space shot rocket]
)<fig:flight_sim>

== Engine sim

To simulate our engine we are using the "Nitrous Engine Sim" developed by Rick Newland  @rick_2011 @rick_2017 @rick_2025 with some additional augmentations by us. The sim uses thermophysical combustion properties of a given fuel combination calculated through
the propep 3 software @propep_3 and combines with regression rate formulas as well engine geometry considerations such as injector and nozzle geometry.

As a fuel we choose to use paraffin wax. It has the advantage of higher regression rate, higher specific impulse as well as a lower optimal oxidizer to fuel ratio compared to the other common hybrid fuel HDPE [citation needed].

As Nitrous Engine Sim did previously not support paraffin wax as a fuel choice we first had to add it by generating appropriate values using Propep 3. Propep 3, to our knowledge, does not have an option for paraffin wax, we instead choose petroleum jelly (petrolatum) as chemically close substitute. We then generated values for various pressures and oxidizer to fuel ratios. The specific impulse an combustion
temperatures generated through this can be found in @fig:paraffin_behavior.

#figure(
    grid(columns: 2, image("../output/chemistry/paraffin_petrogel_OF_ISP.png"), image("../output/chemistry/paraffin_petrogel_OF_T.png"))
    ,
    caption: [
        Theoretical specific impulse and combustion temperature of Nitrous oxide and petroleum jelly
        ]
)<fig:paraffin_behavior>

Besides the combustion behavior of the propellant mix the regression rate of the fuel grain needs to be known to design an engine. The generally accepted formula @rick_2017 for the regression rate is:

$
  dot(r)(x) = a G_"ox"^n x^m
$ <eq:regression_rate>

where $G_"ox"$ is oxygen flux through the engine, $x$ the position along the grain and $a$ as well as $n$ are constant which get experimentally determined. As a simplification we assume that $m = 0$ in our simulations.
As the parameters $a$ and $n$ are empirical there is no good agreement on what they are exactly. It has been observed that they depend on a range of factors, like pressure, engine geometry and the exact composition of paraffin used @zilliac @stanford_regression_rate. A further factor to why these numbers differ is that the experimental numbers that have been obtained aren't very exact and the resulting values of $a$ and $n$ are dependent on the exact fit used. @fig:fitted_regression_rate illustrates this. 

#figure(
    image("../output/r2s_2026/stanford_regression_rate.png"),
    caption: [Pure paraffin experimental regression rates obtained by Eric Dorian et. al. @stanford_regression_rate and fitted using @eq:regression_rate]
) <fig:fitted_regression_rate>

Due to this ambiguity we choose to model our potential engine with multiple regression rate numbers in mind. @ta:regression_rates shows a range of regression rates for paraffin+nitrous found in literature. 

#figure(
    table(
        columns: 5,
        rows:7,
        [$a$ (mm/s)], [$n$], [Source], [Citation], [Method],
        [$0.700$], [$0.2605$], [Eric Dorian et. al.], [@stanford_regression_rate], [Our fit],
        [$0.210$], [$0.5$], [Eric Dorian et. al.], [@stanford_regression_rate], [Our fit, fixing $n=0.5$],
        [$0.155$], [$0.5$], [Anthony McCormick et. al.], [@full_hybrid_design_paper], [Numbers based on Eric Dorian et. al. @stanford_regression_rate],
        [$0.104$], [$0.67$], [Shani Sisi & Alon Gany], [@iit_regression_rate], [Their fit],
        [$0.0876$], [$0.3953$], [Lin-lin Liu et. al.], [@linliu], [Their fit],
        [$0.0488$], [$0.5$], [Lin-lin Liu et. al.], [@linliu], [Our fit, fixing $n=0.5$]
    ),
    caption: [Regression rates from literature]
) <ta:regression_rates>

Our main aim with this engine is to maximize ISP, 


Based on the fuel mass, an optimal ox ratio of 1:6, for nitrous and HDPE we can then calculate the fuel grain length using:




$

// V = l pi (r^2-r_p^2) \

// m = rho V \

// m = rho l pi (r^2-r_p^2) \

l = m_("fuel")/(rho_("HDPE") pi (r^2-r_p^2)) \

$

where $r$ is the fuel grain outer diameter and $r_p$ the initial port size cut into the fuel. The outer diameter of the grain is govenered by available phenolic liners (more on this later). For this initial calculation we are going with the PT-3.9 by Blackcat Rocketry @blackcat, with an outer diameter of $r approx (99"mm")/2$. As an initial port size we are using $r_p = 15 "mm"$ based on successful ignition and operation with our previous motor. This gives us a fuel grain length of $l approx 450"mm" $.

#figure(
    table(
        columns: 2,
        rows:7,
        [Paramter], [Value],
        [Pre combustion chamber length], [$0.06 "mm"$],
        [Post combustion chamber length], [$0.04 "mm"$],
        [Nozzle efficiency], [1],
        [Nozzle area ratio], [3],
        [Engine orifice number], [5],
        [Ox pressure], [$50 "bar"$],
    ),
    caption: [Engine simulation parameters]
) <ta:engine_paramters>

Simulating an engine with parameters from @ta:engine_paramters
results in the performance paramters seen in @fig:engine_mapped

#figure(
    image("../output/r2s_2026/explore_engine.png"),
    caption: [Engine simulated for different ox injector radii and nozzle areas],
    ) <fig:engine_mapped>



#bibliography("all.bib", style: "ieee")
