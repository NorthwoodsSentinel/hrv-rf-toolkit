Public Module Constants

	Public Const TRACE_WIDTH = 3		' width of the system's traces
    Public Const THICK_TRACE = 5        ' width of the system's traces
    Public Const TRACE_COUNT = 6        ' vertical dimension of the data array

	Public Const SAMPLES_PER_SECOND = 256
	Public Const MINIMUM_TICK_SPACING = 100	'pixels
	Public Const LOOKAHEAD_SECONDS = 3
    Public Const LOOKAHEAD_SAMPLES = LOOKAHEAD_SECONDS * SAMPLES_PER_SECOND
	Public Const SINE_FIT_SECONDS = 60

    Public Const YSCALE = 150
    Public Const HRV_SPAN = SAMPLES_PER_SECOND * 4

	Public LAST_SAMPLE = 0 ' 480 * SAMPLES_PER_SECOND ' 10000

	Public BreathOnly As Boolean = False
	Public Monochrome As Boolean = True
	Public TimeScale As Boolean = True

	Public FirstSample, LastSample, HeaderItems As Integer

    Public SampleCount, RwaveCount, RmsCount, RwaveNumber, RmsIndex As Integer
	Public ResonanceBpm, ProgressBar As Double

    Public RwaveTime(1), RwaveVal(1), RwaveVals(1) As Double
	Public RRTime(1), RRVal(1), RRVals(1) As Double

	Public SampleSet As Array
	Public BreathSamples As Array

    Public PeakTime(1), LastPeak As Integer
    Public PeakVal(1) As Double
	Public PeakPoint As Integer

	Public PeakBreathTimes() As Integer
	Public PeakBreathVals() As Double
	Public LastBreathPeak As Integer = 0
	Public BRVal(), BRVals(), BRAvg, BRrms As Double

	Public DeltaTimes(), DeltaVals() As Double
	Public DeltaIndex As Integer

	'Public BreathEventTime(1) As Integer	' location of midpoint between successive breath events
	'Public BreathEventVal(1) As Integer		' value of the sample distance between successive breath events
	'Public BreathEventPeriods(1) As Integer	' lowess-smoothed distances between successive breath events
	'Public LastBreathEvent As Integer		' the index of the last Breath event

	Public FileProcessed = False
	Public SessionLabel As String
	Public NameProcessed As String

End Module

