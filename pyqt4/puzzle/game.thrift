namespace cpp game
namespace php game
namespace py game

struct Result
{
	1: i32 code
	2: string msg
}


struct EDState
{
	1: string chess
	2: i32 row
	3: i32 col
}

struct EDRandomState
{
	1: Result res
	2: EDState randomState
}

struct EDSolution
{
	1: Result res
	2: list<i32> directions
}

service EightDigital
{
	EDRandomState getRandomState(1: EDState _start, 2: i32 steps);
	EDSolution getSolution(1: EDState _start, 2: EDState _end, 3: i32 msWaitTime);
}
