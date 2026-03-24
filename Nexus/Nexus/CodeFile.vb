Public Module ProcessingCode

	Public SourceFile As String

    Public Sub ProcessData(ByRef SourceFile As String)

		'-----------------------------------------------------------------------
		If (BreathOnly) Then
			Processing.Label13.Text = "Loading Breaths"
		Else
			Processing.Label13.Text = "Loading File..."
		End If

		Application.DoEvents()
		'-----------------------------------------------------------------------

		' this gets the file's sample count and also grabs data from the file header
		SampleCount = GetSampleCount(SourceFile)

		If HeaderItems <> 6 Then
			MsgBox("That was not a valid Nexus export file.")
			Exit Sub
		End If

		If LAST_SAMPLE <> 0 Then SampleCount = LAST_SAMPLE + 1

		'-----------------------------------------------------------------------
		Processing.Label13.Text = SampleCount.ToString("N0")
		Processing.Label14.Text = (SampleCount / 256).ToString("N0")
		Processing.Label15.Text = (SampleCount / 256 / 60).ToString("N2")
		Application.DoEvents()
		'-----------------------------------------------------------------------

		Dim LocalSampleSet(SampleCount, TRACE_COUNT)
		SampleSet = LocalSampleSet

		'-----------------------------------------------------------------------
		If (BreathOnly) Then
			Processing.Label16.Text = "Reloading Breaths"
		Else
			Processing.Label16.Text = "Reloading File..."
		End If
		Application.DoEvents()
		'-----------------------------------------------------------------------

		GetSampleSet(SourceFile)

		'-----------------------------------------------------------------------
		Processing.Label16.Text = ""
		Processing.ProgressBar1.Visible = True					' show the bar
		Application.DoEvents()
		'-----------------------------------------------------------------------

		FirstSample = 0
		LastSample = SampleCount - 1
		'RunWorker(New System.Threading.Thread(AddressOf SanityCheckAndTrimSampleSet), Processing.ProgressBar1)

		'-----------------------------------------------------------------------
		Processing.ProgressBar1.Visible = False					' hide the bar
		Processing.Label16.Text = SampleCount.ToString("N0")	' show the results
		Application.DoEvents()
		'-----------------------------------------------------------------------

		LAST_SAMPLE = SampleCount - 1

		FilterBreathData()	' A 0.05Hz high-pass filter to remove DC bias from the breathing data
		FindBreathPeaks()
		MeasureBreathExcursions()

		RunWorker(New System.Threading.Thread(AddressOf Process_Raw_EKG), Processing.ProgressBar2)
		RunWorker(New System.Threading.Thread(AddressOf RemoveEctopicBeats), Processing.ProgressBar3)
		RwaveCount = GetRwaveCount()

		'-----------------------------------------------------------------------
		Processing.Label18.Text = RwaveCount
		Application.DoEvents()
		'-----------------------------------------------------------------------

		Array.Resize(RwaveTime, RwaveCount)
		Array.Resize(RwaveVal, RwaveCount)
		Array.Resize(RwaveVals, RwaveCount)
		Array.Resize(RRVal, RwaveCount)

		BuildRwaveArrays()

		' find the first rwave at or after sample 99000
		'Dim n = 0
		'Do Until RwaveTime(n) >= 99000
		'n = n + 1
		'Loop

		' dump five seconds of rwave
		'Do Until RwaveTime(n) >= (99000 + 5 * SAMPLES_PER_SECOND)
		'Console.WriteLine("Rwave Time: " & RwaveTime(n) & ", RwaveVal: " & RwaveVal(n) & ", R-R Interval:" & RwaveTime(n - 1))
		'n = n + 1
		'Loop

		RunWorker(New System.Threading.Thread(AddressOf RebaseAndInvertRwaves), Processing.ProgressBar4)

		FindHrvPeaks()

		'-----------------------------------------------------------------------
		Processing.Label19.Text = LastPeak + 1
		Application.DoEvents()
		'-----------------------------------------------------------------------

		RunWorker(New System.Threading.Thread(AddressOf MeasurePeakToPeak), Processing.ProgressBar5)

		'-----------------------------------------------------------------------
		Processing.Label20.Text = PeakPoint.ToString("N0")
		Console.WriteLine("Excursion peak at sample: " & PeakPoint.ToString("N0"))
		Application.DoEvents()
		'-----------------------------------------------------------------------

		'FindBreathPeaks()
		'MeasureBreathExcursions()

		'CalcDeltaCurve()

		RescaleBR()
		RescaleHR()

		'=============
		SineWaveFit()
		'=============

		FileProcessed = True

	End Sub
	Sub RunWorker(ByVal Worker As System.Threading.Thread, ByVal ProgBar As Object)
		ProgressBar = 0	' we start with the public value at zero 
		Worker.Start()
		Do
			ProgBar.Value = ProgressBar
			Application.DoEvents()
		Loop Until Worker.Join(5)
		ProgBar.Value = ProgressBar
		Application.DoEvents()
	End Sub
	Function GetSampleCount(ByRef SourceFile As String) As Integer

		Dim InData = False, SampleCount = 0
		Dim Line As String

		If InStr(SourceFile, ".dat") Then
			InData = True
		End If

		Using LineIn As New FileIO.TextFieldParser(SourceFile)
			LineIn.TextFieldType = FileIO.FieldType.Delimited
			LineIn.SetDelimiters(",", vbTab)
			While Not LineIn.EndOfData
				If InData Then
					Try
						Dim DatumCount = LineIn.ReadFields().Length
						If DatumCount >= 2 And DatumCount <= 4 Then SampleCount = SampleCount + 1
					Catch
					End Try
				Else
					Line = LineIn.ReadLine
					If String.Compare(Left(Line, 6), "Client") = 0 Then HeaderItems = HeaderItems + 1
					If String.Compare(Left(Line, 7), "Session") = 0 Then HeaderItems = HeaderItems + 1
					If String.Compare(Left(Line, 4), "Date") = 0 Then HeaderItems = HeaderItems + 1
					If String.Compare(Left(Line, 4), "Time") = 0 Then HeaderItems = HeaderItems + 1
					If String.Compare(Left(Line, 11), "Output rate") = 0 Then
						HeaderItems = HeaderItems + 1
						If Line.Contains("256") Then HeaderItems = HeaderItems + 1
					End If
					If String.Compare(Left(Line, 6), "Sensor") = 0 Then InData = True
				End If
				Application.DoEvents()
			End While
		End Using

		Return SampleCount

	End Function
	Sub GetSampleSet(ByRef SourceFile As String)

		Dim InData = False, SampleNumber = 0

		If InStr(SourceFile, ".dat") Then
			InData = True
		End If

		Using LineIn As New FileIO.TextFieldParser(SourceFile)
			LineIn.TextFieldType = FileIO.FieldType.Delimited
			LineIn.SetDelimiters(",", vbTab)
			While Not LineIn.EndOfData
				If InData Then
					Try
						Dim Datums = LineIn.ReadFields()
						If Datums.Length >= 2 And Datums.Length <= 4 Then
							SampleSet(SampleNumber, 0) = Datums(0)
							SampleSet(SampleNumber, 1) = Datums(1)
							SampleNumber = SampleNumber + 1
							If SampleNumber >= SampleCount Then Exit Sub
							Application.DoEvents()
						End If
					Catch
					End Try
				Else
					If String.Compare(Left(LineIn.ReadLine, 6), "Sensor") = 0 Then InData = True
				End If
			End While
		End Using

	End Sub
	Sub SanityCheckAndTrimSampleSet()
		' this looks at the middle 60% of the session data to obtain the range
		' of valid data for both channels. It then hunts outward from either
		' end to the first sample which falls outsidee of the range found.

		Dim HR_Max = Double.MinValue, HR_Min = Double.MaxValue
		Dim BR_Max = Double.MinValue, BR_Min = Double.MaxValue
		Dim FirstSample As Integer = SampleCount * 0.2		  ' we don't initially scan the first 20%
		Dim LastSample As Integer = SampleCount - FirstSample ' we don't initially scan the final 20%
		Dim UpdateInterval = SampleCount / 100

		For n = FirstSample To LastSample
			If SampleSet(n, 0) > HR_Max Then HR_Max = SampleSet(n, 0)
			If SampleSet(n, 0) < HR_Min Then HR_Min = SampleSet(n, 0)
			If SampleSet(n, 1) > BR_Max Then BR_Max = SampleSet(n, 1)
			If SampleSet(n, 1) < BR_Min Then BR_Min = SampleSet(n, 1)
			ProgressBar = (n - FirstSample) / UpdateInterval
		Next

		' now we expand the acceptable range of the Min and Max by 50%
		Dim HR_Range = (HR_Max - HR_Min) / 2	' get half of the difference between them
		Dim BR_Range = (BR_Max - BR_Min) / 2
		HR_Max = HR_Max + HR_Range				' move the upper up by that half-diff
		HR_Min = HR_Min - HR_Range
		BR_Max = BR_Max + BR_Range				' move the lower down by that half-diff
		BR_Min = BR_Min - BR_Range

		' now we scan left from the left edge to find the first out-of-range sample sets
		Do
			FirstSample = FirstSample - 1
			If SampleSet(FirstSample, 0) > HR_Max Then Exit Do
			If SampleSet(FirstSample, 0) < HR_Min Then Exit Do
			If SampleSet(FirstSample, 1) > BR_Max Then Exit Do
			If SampleSet(FirstSample, 1) < BR_Min Then Exit Do
			ProgressBar = (LastSample - FirstSample) / UpdateInterval
		Loop While FirstSample > 0

		' now we scan right from the right edge to find the first out-of-range sample sets
		Do
			If SampleSet(LastSample, 0) > HR_Max Then Exit Do
			If SampleSet(LastSample, 0) < HR_Min Then Exit Do
			If SampleSet(LastSample, 1) > BR_Max Then Exit Do
			If SampleSet(LastSample, 1) < BR_Min Then Exit Do
			ProgressBar = LastSample / UpdateInterval
			LastSample = LastSample + 1
		Loop While LastSample < (SampleCount - 1)

		ProgressBar = 100	' leave the ProgressBar

		SampleCount = LastSample - FirstSample + 1	' update our sample count

		' we =do= have something to trim from the front of the array,
		' so let's copy the first valid sample down to the front of the array...
		For n = 0 To SampleCount - 1
			SampleSet(n, 0) = SampleSet(n + FirstSample, 0)
			SampleSet(n, 1) = SampleSet(n + FirstSample, 1)
		Next
	End Sub
	Sub FilterBreathData()
		' This is a high-pass filter with a very low corner frequency of 0.05Hz
		' (20 second response time). It is used to AC-couple the breathing to
		' normalize and bring it down to a zero centerline. It is designed to
		' introduce negligible phase shift into the breath data.
		'
		' https://www-users.cs.york.ac.uk/~fisher/mkfilter/trad.html
		' 
		' Chebyshev - Highpass - 256 samples/sec - (-1 dB ripple) Corner Freq 0.05Hz

		Dim xv0, xv1, yv0, yv1 As Double
		Dim RmsCount = 0

		BRrms = 0				' init the RMS summation
		xv1 = SampleSet(0, 1)

		For n = 0 To LAST_SAMPLE
			xv0 = xv1
			xv1 = SampleSet(n, 1) / 1.000312225
			yv0 = yv1
			yv1 = xv1 - xv0 + 0.9993757454 * yv0
			SampleSet(n, 1) = yv1
			If (n > 30 * SAMPLES_PER_SECOND) Then
				BRrms = BRrms + (yv1 * yv1)
				RmsCount = RmsCount + 1
			End If
		Next

		' calculate the RMS power value
		BRrms = Math.Sqrt(BRrms / RmsCount)

	End Sub
	Sub Process_Raw_EKG()
		' This takes in the raw EKG and returns an Array of inter-beat intervals

		' 0: Raw HR Source Data
		' 2: dv/dt encoded HR
		' 3: ROI (region of interest) data
		' 4: R-Wave Point

		' INPUT: 0 / OUTPUT: 1

		Dim t0, t1, t2 As Double
		'
		' This is a weighted dv/dt differentiator functioning as a history-weighted high-pass
		' filter to move the EKG's DC component and preferentially feature-extract the R-Wave 
		' 
		t0 = t1 = t2 = SampleSet(0, 0)
		For n = 3 To LAST_SAMPLE
			SampleSet(n - 3, 2) = (t0 * 1.0 + t1 * 0.5 + t2 * 0.25) / 1.75 - SampleSet(n, 0)
			t0 = t1
			t1 = t2
			t2 = SampleSet(n, 0)
			ProgressBar = (n / LAST_SAMPLE) * 45
		Next

		' forensic dump
		'WriteRtoRintervalFile(SourceFile, 2)

		'
		' This performs a 5-point center-average to ignore noise and determine
		' ROI's (regions of interest) which we then use to detect R-wave maxima
		'
		For n = 2 To LAST_SAMPLE - 2
			SampleSet(n, 3) = (SampleSet(n - 2, 2) + SampleSet(n - 1, 2) + SampleSet(n, 2) + SampleSet(n + 1, 2) + SampleSet(n + 2, 2)) / 5
			ProgressBar = (n / LAST_SAMPLE) * 45 + 45
		Next

		Dim ScanPoint, PeakPoint, Rmax, Rpoint, PriorRpoint, InterbeatSamples As Integer, PeakMax As Double

		' we begin by finding the first R-wave in the trace
		ScanPoint = 0
		PeakMax = Double.MinValue
		For n = ScanPoint To ScanPoint + LOOKAHEAD_SAMPLES - 1
			If (SampleSet(n, 3) > PeakMax) Then
				PeakMax = SampleSet(n, 3)
				PeakPoint = n
			End If
		Next

		PriorRpoint = 0	' show that we don't yet have a previous Rmax

		' we scan forward searching for the first ROI value that's at least 70% of the prior peak
		Do
			PeakMax = PeakMax * 0.7
			PeakPoint = 0

PeakSearch: For n = ScanPoint To ScanPoint + LOOKAHEAD_SAMPLES - 1
				If (SampleSet(n, 3) > PeakMax) Then
					PeakMax = SampleSet(n, 3)
					PeakPoint = n
				ElseIf (PeakPoint) Then
					Exit For
				End If
			Next

			' if we did not find a local qualifting peak point we scale down our search and retry
			If (PeakPoint = 0) Then
				PeakMax = PeakMax * 0.95
				GoTo PeakSearch
			End If

			' now we locate the maximum Delta-coded R-wave within 2 samples either side of the ROI peak
			Rmax = 0
			For n = PeakPoint - 2 To PeakPoint + 2
				If SampleSet(n, 2) > Rmax Then
					Rmax = SampleSet(n, 2)
					Rpoint = n
				End If
			Next


			If PriorRpoint Then
				InterbeatSamples = Rpoint - PriorRpoint
				SampleSet(Rpoint, 4) = InterbeatSamples
			End If

			PriorRpoint = Rpoint

			' bump the scanner forward 20 samples past this R-wave
			ScanPoint = Rpoint + 20

			ProgressBar = (ScanPoint / LAST_SAMPLE) * 10 + 90

		Loop While (ScanPoint + LOOKAHEAD_SAMPLES) < LAST_SAMPLE

	End Sub
	Sub RemoveEctopicBeats()
		' This removes ectopic beats from the R-R interval array. It takes Array #4, as runs of interbeat intervals
		' It takes four interbeat intervals 

		Dim Scanner, PreviousRun, Anchor1, Anchor2, Anchor3, ThisRun, Delta1, Delta2, Delta3 As Integer

		' zero our #3 Results Array
		For n = 0 To LAST_SAMPLE
			SampleSet(n, 3) = 0
		Next

		' find the start of the IBI data (scan from '0' to the first non)
ReDo:   Scanner = 0
		Do Until SampleSet(Scanner, 4) <> 0
			Scanner = Scanner + 1
		Loop

		PreviousRun = 0

NextRun:

		Anchor1 = Anchor2
		Anchor2 = Anchor3
		Anchor3 = Scanner					 ' drop an anchor at the start of the run

		Do
			Scanner = Scanner + 1
		Loop Until (SampleSet(Scanner, 4)) Or (Scanner >= LAST_SAMPLE)

		ThisRun = Scanner - Anchor3

		If PreviousRun Then

			Delta1 = Delta2					' oldest delta
			Delta2 = Delta3
			Delta3 = ThisRun - PreviousRun	' newest delta

			' check for a posible PVC pattern in interbeat differences
			If Delta1 < 0 And Delta2 > 0 And Delta3 < 0 Then
				If Math.Abs(Delta2 + Delta1 + Delta3) < (Delta2 * 0.1) Then
					SampleSet(Anchor2, 4) = 0
					Anchor2 = Int((Anchor1 + Anchor3) / 2)
					SampleSet(Anchor2, 4) = (Anchor2 - Anchor1)
					SampleSet(Anchor3, 4) = (Anchor3 - Anchor2)
					GoTo ReDo
				End If
			End If
		End If

		PreviousRun = ThisRun
		ProgressBar = Scanner / LAST_SAMPLE * 100
		If (Scanner < LAST_SAMPLE) Then GoTo NextRun

	End Sub
	Function GetRwaveCount() As Integer

		' Input #4: R-wave events where value is non-zero. Has distance from previous R-wave event

		Dim ScanPoint As Integer, RwaveCount As Integer = 0

		' scan the entire sample field locating and counting Rwave events

		For ScanPoint = 0 To LAST_SAMPLE
			If SampleSet(ScanPoint, 4) Then RwaveCount = RwaveCount + 1
		Next

		Return RwaveCount

	End Function
	Sub BuildRwaveArrays()

		RwaveNumber = 0

		For ScanPoint = 0 To LAST_SAMPLE

			If SampleSet(ScanPoint, 4) Then
				RwaveTime(RwaveNumber) = ScanPoint
				RwaveVal(RwaveNumber) = SampleSet(ScanPoint, 4)
				RwaveNumber = RwaveNumber + 1
			End If

		Next
		RwaveNumber = RwaveNumber - 1

	End Sub
	Sub WriteRtoRintervalFile(ByVal SourceFile As String, ByVal SampleColumn As Integer)

		Dim RRintervalFile = Replace(SourceFile, ".txt", "-rr.dat")

		Dim file = My.Computer.FileSystem.OpenTextFileWriter(RRintervalFile, False, System.Text.Encoding.ASCII)
		For n = 99000 To 100000
			file.WriteLine(SampleSet(n, SampleColumn))
		Next
		file.Close()
		End

	End Sub
	Sub RebaseAndInvertRwaves()
		' This brings the r-wave intervals to a flat baseline. Lowess smoothing
		' is used to create a phase-neutral tracking curve from which individual
		' r-wave intervals are subtracted.

		Lowess2(RwaveTime, RwaveVal, RwaveVals, 41)

		For i = 0 To RwaveCount - 1
			RwaveVal(i) = RwaveVals(i) - RwaveVal(i)
		Next

	End Sub
	Sub FindHrvPeaks()
		' This scans the <RwaveTime|Rwave Val> array pair to alternatively
		' locate the maximum and minimum heart rate value. When found, the
		' <Time|Val> are placed into the <PeakTimes|PeakVals> array pair.

		Dim LocalMax, CurrentVal As Double
		Dim PeakIndex As Integer, CurrentIndex As Integer = 0
		Dim PeakTimes, PeakVals As New Collection

		' search for positive maximum before next zero-crossing
PosPeak: LocalMax = Double.MinValue
		Do
			CurrentVal = RwaveVal(CurrentIndex)
			If CurrentVal > LocalMax Then
				LocalMax = CurrentVal
				PeakIndex = RwaveTime(CurrentIndex)
			End If
			CurrentIndex = CurrentIndex + 1
			If CurrentIndex > (RwaveCount - 1) Then GoTo BuildArrays
		Loop Until CurrentVal < 0

		PeakTimes.Add(PeakIndex)
		PeakVals.Add(LocalMax)

		' search for negative maximum before next zero-crossing
NegPeak: LocalMax = Double.MaxValue
		Do
			CurrentVal = RwaveVal(CurrentIndex)
			If CurrentVal < LocalMax Then
				LocalMax = CurrentVal
				PeakIndex = RwaveTime(CurrentIndex)
			End If
			CurrentIndex = CurrentIndex + 1
			If CurrentIndex > (RwaveCount - 1) Then GoTo BuildArrays
		Loop Until CurrentVal > 0

		PeakTimes.Add(PeakIndex)
		PeakVals.Add(LocalMax)

		GoTo PosPeak

		' having built adhoc collections of the times & vals, we
		' get the count, resize the permanent arrays, enumerate the
		' collections into the arrays, and discard the collections

BuildArrays:

		Array.Resize(PeakTime, PeakTimes.Count)
		Array.Resize(PeakVal, PeakVals.Count)

		Dim TimesEnum As IEnumerator = PeakTimes.GetEnumerator()
		Dim ValsEnum As IEnumerator = PeakVals.GetEnumerator()

		CurrentIndex = 0
		While TimesEnum.MoveNext() And ValsEnum.MoveNext()
			PeakTime(CurrentIndex) = TimesEnum.Current
			PeakVal(CurrentIndex) = ValsEnum.Current
			CurrentIndex = CurrentIndex + 1
		End While
		LastPeak = CurrentIndex - 1

	End Sub
	Sub MeasurePeakToPeak()

		Dim RRScale As Double

		Array.Resize(RRVal, LastPeak)
		Array.Resize(RRVals, LastPeak)

		Dim RRMax = Double.MinValue
		Dim RRMin = Double.MaxValue

		For n = 0 To LastPeak - 1
			RRVal(n) = Math.Abs(PeakVal(n) - PeakVal(n + 1))
		Next

		'Lowess2(PeakTime, RRVal, RRVals, 21)
		Lowess2(PeakTime, RRVal, RRVals, 17)
		'Lowess2(PeakTime, RRVal, RRVals, 13)

		For n = 4 To LastPeak - 1
			If RRVals(n) > RRMax Then RRMax = RRVals(n)
			If RRVals(n) < RRMin Then RRMin = RRVals(n)
		Next

		RRScale = 1.98 * YSCALE / (RRMax - RRMin)

		' now we find the location of the largest RRVal[]
		RRMax = Double.MinValue

		For n = 0 To LastPeak - 1
			RRVal(n) = (RRVals(n) - RRMin) * RRScale - YSCALE
			If RRVal(n) > RRMax Then
				RRMax = RRVal(n)
				PeakPoint = PeakTime(n)
			End If
		Next

	End Sub
	Sub RescaleBR()

		Dim BR_Max = Double.MinValue, BR_Min = Double.MaxValue, BR_Scale As Double

		For n = 0 To LAST_SAMPLE
			If SampleSet(n, 1) > BR_Max Then BR_Max = SampleSet(n, 1)
			If SampleSet(n, 1) < BR_Min Then BR_Min = SampleSet(n, 1)
		Next

		If BR_Max < -BR_Min Then BR_Max = -BR_Min

		BR_Scale = YSCALE / BR_Max * 0.98

		For n = 0 To LAST_SAMPLE
			SampleSet(n, 1) = SampleSet(n, 1) * BR_Scale
		Next

	End Sub
	Sub RescaleHR()

		Dim HR_Max = Double.MinValue, HR_Min = Double.MaxValue, HR_Scale As Double

		For n = 0 To RwaveCount - 1
			If RwaveVal(n) > HR_Max Then HR_Max = RwaveVal(n)
			If RwaveVal(n) < HR_Min Then HR_Min = RwaveVal(n)
		Next

		If HR_Max < -HR_Min Then HR_Max = -HR_Min

		HR_Scale = YSCALE / HR_Max * 0.98

		For n = 0 To RwaveCount - 1
			RwaveVal(n) = RwaveVal(n) * HR_Scale
		Next

	End Sub
	Function GetError(ByVal Phase As Double, ByVal Omega As Double, ByVal Amplitude As Double, ByVal Offset As Double, ByVal FirstSample As Integer, ByVal LastSample As Integer, ByRef SampleSet As Array)

		GetError = 0.0
		For n = FirstSample To LastSample
			GetError = GetError + Math.Abs(Amplitude * Math.Cos(Phase) + Offset - SampleSet(n, 1))
			Phase = Phase + Omega				' advance our osccillator
		Next n

	End Function
	Sub SineWaveFit()

		Dim Light(3) As Object
		Light(0) = Processing.Label21
		Light(1) = Processing.Label22
		Light(2) = Processing.Label23
		Light(3) = Processing.Label24

		' set the starting point for our sine fit
		Dim FirstSample = PeakPoint - (SAMPLES_PER_SECOND * SINE_FIT_SECONDS / 2)
		If FirstSample < 0 Then FirstSample = 0

		'Do While FirstSample < 0
		'FirstSample = FirstSample + SAMPLES_PER_SECOND
		'Loop

		' set the ending point for our sine fit
		Dim LastSample = PeakPoint + (SAMPLES_PER_SECOND * SINE_FIT_SECONDS / 2)
		If LastSample > (SampleCount - 1) Then LastSample = SampleCount - 1

		'Do While LastSample > LAST_SAMPLE
		'LastSample = LastSample - SAMPLES_PER_SECOND
		'Loop

		' we begin by estimating the amplitude and offset with a min & max
		Dim Max = Double.MinValue, Min = Double.MaxValue
		For n = FirstSample To LastSample
			If SampleSet(n, 1) > Max Then Max = SampleSet(n, 1)
			If SampleSet(n, 1) < Min Then Min = SampleSet(n, 1)
		Next

		Dim CosScale = (Max - Min) / 2
		Dim CosOffset = (Max + Min) / 2
		Dim Omega As Double
		Dim Phase = 0.0
		Dim Pi = Math.PI			' get Pi for our use.

		' we first perform a quick crude test for the frequency and phase
		Dim MinError = Double.MaxValue
		Dim MinPhase, MinOmega, LastError As Double
		Dim Lit = 0

		For i = 3.5 To 7.0 Step 0.5
			For j = 0 To 1
				Light(0).BackColor = Color.Transparent
				Light(1).BackColor = Color.Transparent
				Light(2).BackColor = Color.Transparent
				Light(3).BackColor = Color.Transparent
				Light(Lit Mod 4).BackColor = Color.Blue
				Lit = Lit + 1
				Application.DoEvents()

				Omega = 2 * Pi / 60 * i / SAMPLES_PER_SECOND
				LastError = GetError(Pi * j, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)
				If LastError < MinError Then
					MinError = LastError
					MinPhase = Pi * j
					MinOmega = Omega
				End If
			Next
		Next

		Phase = MinPhase
		Omega = MinOmega

		'If NameProcessed.Contains("SA95") Then
		'Omega = 0.00199401015062864
		'Phase = -0.691150383789755
		'CosScale = 71.1325949727345
		'CosOffset = 0.353491656411002
		'End If

SearchPhase:

		Dim Corrections = 0

		Light(0).BackColor = Color.LawnGreen
		Light(1).BackColor = Color.Transparent
		Light(2).BackColor = Color.Transparent
		Light(3).BackColor = Color.Transparent
		Processing.Label25.Text = "---"
		Application.DoEvents()

		LastError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)

		Dim PhaseStep = Pi / 100
		If LastError < GetError(Phase + PhaseStep, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet) Then
			PhaseStep = -PhaseStep
		End If

		For i = 1 To 200
			Phase = Phase + PhaseStep
			Dim ThisError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)
			If LastError < ThisError Then Exit For
			LastError = ThisError
			Corrections = Corrections + 1
			Processing.Label21.BackColor = Color.Red
			Processing.Label25.Text = i
			Application.DoEvents()
		Next i
		Phase = Phase - PhaseStep

		' Adjust Frequency
		Light(1).BackColor = Color.LawnGreen
		Processing.Label25.Text = "---"
		Application.DoEvents()

		LastError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)

		Dim OmegaStep = 1.001
		If LastError < GetError(Phase, Omega * OmegaStep, CosScale, CosOffset, FirstSample, LastSample, SampleSet) Then
			OmegaStep = 1 / OmegaStep
		End If

		For i = 1 To 400
			Omega = Omega * OmegaStep
			Dim ThisError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)
			If LastError < ThisError Then Exit For
			LastError = ThisError
			Corrections = Corrections + 1
			Processing.Label22.BackColor = Color.Red
			Processing.Label25.Text = i
			Application.DoEvents()
		Next i
		Omega = Omega / OmegaStep

		' Adjust DC Offset
		Light(2).BackColor = Color.LawnGreen
		Processing.Label25.Text = "---"
		Application.DoEvents()

		LastError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)

		Dim OffsetStep = 1
		If LastError < GetError(Phase, Omega, CosScale, CosOffset + OffsetStep, FirstSample, LastSample, SampleSet) Then
			OffsetStep = -1
		End If

		For i = 1 To 200
			CosOffset = CosOffset + OffsetStep
			Dim ThisError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)
			If LastError < ThisError Then Exit For
			LastError = ThisError
			Corrections = Corrections + 1
			Processing.Label23.BackColor = Color.Red
			Processing.Label25.Text = i
			Application.DoEvents()
		Next i
		CosOffset = CosOffset - OffsetStep

		'Adjusting Amplitude
		Light(3).BackColor = Color.LawnGreen
		Processing.Label25.Text = "---"
		Application.DoEvents()

		LastError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)

		Dim AmplitudeScale = 1.005
		If LastError < GetError(Phase, Omega, CosScale * AmplitudeScale, CosOffset + OffsetStep, FirstSample, LastSample, SampleSet) Then
			AmplitudeScale = 1 / AmplitudeScale
		End If

		For i = 1 To 999
			CosScale = CosScale * AmplitudeScale
			Dim ThisError = GetError(Phase, Omega, CosScale, CosOffset, FirstSample, LastSample, SampleSet)
			If LastError < ThisError Then Exit For
			LastError = ThisError
			Corrections = Corrections + 1
			Processing.Label24.BackColor = Color.Red
			Processing.Label25.Text = i
			Application.DoEvents()
		Next i
		CosScale = CosScale / AmplitudeScale

		If Corrections Then GoTo SearchPhase

		'-----------------------------------------------------------------------
		'Console.WriteLine("Omega     = {0}", Omega)
		'Console.WriteLine("Phase     = {0}", Phase)
		'Console.WriteLine("CosScale  = {0}", CosScale)
		'Console.WriteLine("CosOffset = {0}", CosOffset)
		'-----------------------------------------------------------------------

Show:   For n = FirstSample To LastSample
			SampleSet(n, 2) = CosScale * Math.Cos(Phase) + CosOffset
			Phase = Phase + Omega				' advance our osccillator
		Next n

		ResonanceBpm = Omega / 2 / Pi * 60 * SAMPLES_PER_SECOND
		'Console.WriteLine("Calculated actual breaths per minute: {0:0.00}", ResonanceBpm)
	End Sub
	Sub FindBreathPeaks()

		' This scans the breath data (1/8th of the samples since it only changes
		' at 32 samples/second) to alternatively locate the maximum and minimum
		' breath peaks When found, the <Time|Val> are placed into the
		' <PeakBreathTimes | PeakBreathVals> array pair.

		Dim LocalMax, LocalMin, CurrentVal As Double, FilteredVal As Double = 0
		Dim PeakIndex As Integer, CurrentIndex As Integer = 0
		Dim PeakTimes, PeakVals As New Collection

		' first set an initial centerline by averaging the first minute of breathing samples
		For n = 1 To SAMPLES_PER_SECOND * 60
			FilteredVal = FilteredVal + SampleSet(n, 1)
		Next
		FilteredVal = FilteredVal / (SAMPLES_PER_SECOND * 60)

		' search for positive maximum before next zero-crossing
PosPeak: LocalMax = Double.MinValue
		Do
			CurrentVal = SampleSet(CurrentIndex, 1)
			FilteredVal = FilteredVal * 0.99 + CurrentVal * 0.01
			If CurrentVal > LocalMax Then
				LocalMax = CurrentVal
				PeakIndex = CurrentIndex
			End If
			CurrentIndex = CurrentIndex + 8	' skip by 8 samples since 32 sps
			If CurrentIndex > LAST_SAMPLE Then GoTo BuildArrays
			' we search down to half of the previous negative peak value
		Loop Until CurrentVal < FilteredVal

		PeakTimes.Add(PeakIndex)
		PeakVals.Add(LocalMax)

		' search for negative maximum before next zero-crossing
NegPeak: LocalMin = Double.MaxValue
		Do
			CurrentVal = SampleSet(CurrentIndex, 1)
			FilteredVal = FilteredVal * 0.99 + CurrentVal * 0.01
			If CurrentVal < LocalMin Then
				LocalMin = CurrentVal
				PeakIndex = CurrentIndex
			End If
			CurrentIndex = CurrentIndex + 8	' skip by 8 samples since 32 sps
			If CurrentIndex > LAST_SAMPLE Then GoTo BuildArrays
			' we search up to half of the previous positive peak value
		Loop Until CurrentVal > FilteredVal

		PeakTimes.Add(PeakIndex)
		PeakVals.Add(LocalMin)

		GoTo PosPeak

		' having built adhoc collections of the times & vals, we
		' get the count, resize the permanent arrays, enumerate the
		' collections into the arrays, and discard the collections

BuildArrays:

		Array.Resize(PeakBreathTimes, PeakTimes.Count)
		Array.Resize(PeakBreathVals, PeakVals.Count)

		Dim TimesEnum As IEnumerator = PeakTimes.GetEnumerator()
		Dim ValsEnum As IEnumerator = PeakVals.GetEnumerator()

		CurrentIndex = 0
		While TimesEnum.MoveNext() And ValsEnum.MoveNext()
			PeakBreathTimes(CurrentIndex) = TimesEnum.Current
			PeakBreathVals(CurrentIndex) = ValsEnum.Current
			CurrentIndex = CurrentIndex + 1
		End While
		LastBreathPeak = CurrentIndex - 1

	End Sub
	Sub MeasureBreathExcursions()

		Dim BRScale As Double

		Array.Resize(BRVal, LastBreathPeak)
		Array.Resize(BRVals, LastBreathPeak)

		Dim BRMax = Double.MinValue
		Dim BRMin = Double.MaxValue
		Dim BRSum As Double = 0
		Dim BRCnt = 0

		For n = 0 To LastBreathPeak - 1
			BRVal(n) = Math.Abs(PeakBreathVals(n) - PeakBreathVals(n + 1))
			If (PeakBreathTimes(n) > 30 * SAMPLES_PER_SECOND) Then
				BRSum = BRSum + BRVal(n)
				BRCnt = BRCnt + 1
			End If
		Next
		BRAvg = BRSum / BRCnt

		If (BreathOnly) Then
			MsgBox("Average Breathing Amplitude: " & BRAvg.ToString("N2") & vbCrLf & "  Average RMS Breath Power: " & BRrms.ToString("N2") & vbCrLf & "     Session Half-Breath Count: " & LastBreathPeak)
			Processing.Close()							' and terminate ourself
			End
		End If

		'Lowess2(PeakBreathTimes, BRVal, BRVals, 21)
		Lowess2(PeakBreathTimes, BRVal, BRVals, 17)
		'Lowess2(PeakBreathTimes, BRVal, BRVals, 13)

		For n = 4 To LastBreathPeak - 1
			If BRVals(n) > BRMax Then BRMax = BRVals(n)
			If BRVals(n) < BRMin Then BRMin = BRVals(n)
		Next

		BRScale = 1.98 * YSCALE / (BRMax - BRMin)

		For n = 0 To LastBreathPeak - 1
			BRVal(n) = (BRVals(n) - BRMin) * BRScale - YSCALE
		Next

	End Sub
	Sub CalcDeltaCurve()

		Array.Resize(DeltaTimes, LastPeak + LastBreathPeak)
		Array.Resize(DeltaVals, LastPeak + LastBreathPeak)

		Dim HeartIndex As Integer = 0
		Dim BreathIndex As Integer = 0
		DeltaIndex = 0

		If (PeakTime(HeartIndex) < PeakBreathTimes(BreathIndex)) Then GoTo MoveHeart

MoveBreath:

		' breathtime is earlier, so move it forward
		Do While (PeakBreathTimes(BreathIndex) < PeakTime(HeartIndex))
			BreathIndex = BreathIndex + 1
			If BreathIndex > (LastBreathPeak - 1) Then GoTo ScaleDeltas
		Loop

		' we have a new breath-heart delta event
		DeltaTimes(DeltaIndex) = PeakBreathTimes(BreathIndex)
		DeltaVals(DeltaIndex) = RRVal(HeartIndex) - BRVal(BreathIndex)
		DeltaIndex = DeltaIndex + 1

MoveHeart:  ' hearttime is earlier, so move it forward

		Do While (PeakBreathTimes(BreathIndex) > PeakTime(HeartIndex))
			HeartIndex = HeartIndex + 1
			If HeartIndex > (LastPeak - 1) Then GoTo ScaleDeltas
		Loop

		' we have a new breath-heart delta event
		DeltaTimes(DeltaIndex) = PeakTime(HeartIndex)
		DeltaVals(DeltaIndex) = RRVal(HeartIndex) - BRVal(BreathIndex)
		DeltaIndex = DeltaIndex + 1

		GoTo MoveBreath

ScaleDeltas:

		Dim DeltaMax = Double.MinValue
		Dim DeltaMin = Double.MaxValue

		For n = 0 To DeltaIndex - 1
			If DeltaVals(n) > DeltaMax Then DeltaMax = DeltaVals(n)
			If DeltaVals(n) < DeltaMin Then DeltaMin = DeltaVals(n)
		Next

		Dim DeltaScale = 1.98 * YSCALE / (DeltaMax - DeltaMin)

		For n = 0 To DeltaIndex - 1
			DeltaVals(n) = (DeltaVals(n) - DeltaMin) * DeltaScale - YSCALE
		Next

	End Sub
End Module