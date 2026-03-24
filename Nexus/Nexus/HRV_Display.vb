Imports System.IO

Public Class HRV_Display

	Private Sub HrvDisplay_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
		Dim Width As Integer = Screen.PrimaryScreen.Bounds.Width
		Dim Height As Integer = Screen.PrimaryScreen.Bounds.Height

		SessionLabel = "HRVisualizer Analysis of: " & NameProcessed

		Me.Visible = False

		ChartSetup()

		Me.Size = New Size(4 * Width / 5, 2 * Height / 5)
		Me.Left = (Width - Me.Width) / 2
		Me.Top = (Height - Me.Height) / 2
		Me.Text = "HRVisualizer Analysis of: " & NameProcessed & "  /  Average Breath Amplitude: " & BRAvg.ToString("N3")

		HScrollBar.Minimum = FirstSample
		HScrollBar.Maximum = LastSample
		HScrollBar.LargeChange = HScrollBar.Maximum

		Display()
		Me.Visible = True
		Application.DoEvents()

	End Sub
	Private Sub HrvDisplay_Resize(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Resize

		Chart.Left = 25
		Chart.Top = 25 + MenuStrip.Height
		Chart.Size = New Size(Me.Width - 68, Me.Height - (MenuStrip.Height + HScrollBar.Height + 65))

	End Sub
	Private Sub PrintMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles PrintToolStripMenuItems.Click

		Dim pd As System.Drawing.Printing.PrintDocument = Chart.Printing.PrintDocument
		pd.DefaultPageSettings.Landscape = True
		Dim margins As New System.Drawing.Printing.Margins(0, 0, 0, 0)
		pd.DefaultPageSettings.Margins = margins

		Chart.Printing.Print(True)

	End Sub
	Private Sub AutoZoomToolStripMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles AutoZoomToolStripMenuItem.Click
		UpdateDisplay(SAMPLES_PER_SECOND * SINE_FIT_SECONDS * 2, PeakPoint)
	End Sub
	Private Sub EntireSessionToolStripMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles EntireSessionToolStripMenuItem.Click
		UpdateDisplay(SampleCount, SampleCount / 2)
	End Sub
	Sub PrintPreview(ByVal pd As System.Drawing.Printing.PrintDocument)

		' Declare the dialog.
		Dim ppd As PrintPreviewDialog = New PrintPreviewDialog

		'Set the size, location, and name.
		ppd.ClientSize = New System.Drawing.Size(800, 600)
		ppd.Location = New System.Drawing.Point(0, 0)
		ppd.UseAntiAlias = True
		ppd.Document = pd 'Chart.Printing.PrintDocument
		ppd.ShowDialog()

	End Sub
	Public Sub ChartSetup()

		Dim area = Chart.ChartAreas(0)

		area.BorderColor = Color.White
		area.BorderWidth = 0

		area.AxisX.Enabled = 1
		area.AxisX.LineWidth = 1
		area.AxisX.ScrollBar.Enabled = False
		area.AxisX.IsStartedFromZero = False
		area.AxisX.LabelStyle.Enabled = TimeScale

		If (Monochrome) Then
			area.AxisX.Title = ""
		Else
			area.AxisX.Title = SessionLabel	' "Breath Cycle and Heart Rate Variability"
		End If
		area.AxisX.TitleFont = New System.Drawing.Font("Microsoft Sans Serif", 20)
		area.AxisX.TitleForeColor = Color.Green

		area.AxisY.LineWidth = 1
		area.AxisY.ScrollBar.Enabled = False
		area.AxisY.LabelStyle.Enabled = False
		area.AxisY.MajorTickMark.Enabled = False
		area.AxisY.MinorTickMark.Enabled = False
		area.AxisY.IsStartedFromZero = False
		area.AxisY.Maximum = YSCALE * 1.0
		area.AxisY.Minimum = -YSCALE * 1.0

		area.Position.X = 0
		area.Position.Y = 0
		area.Position.Width = 100
		area.Position.Height = 100

	End Sub

	Public Sub AddScaleLabels(ByVal area As DataVisualization.Charting.ChartArea)
		Dim SecondsPerTick, SamplesPerTick As Integer
		Dim NumberOfTicks As Double = Chart.Size.Width / MINIMUM_TICK_SPACING
		Dim NumberOfSeconds As Double = (LastSample - FirstSample) / SAMPLES_PER_SECOND

		Dim Tick_series = Chart.Series.Add("LABEL_TICK")
		With Tick_series
			.Color = Color.LightGray
			.ChartType = DataVisualization.Charting.SeriesChartType.Line
			.BorderDashStyle = DataVisualization.Charting.ChartDashStyle.Dot
			.BorderWidth = 1
		End With

		' this next block successively tests greater nice-value SecondsPerTick,
		' increasing the value until we have fewer than our maximum NumberOfTicks
		SecondsPerTick = 1
		If (NumberOfSeconds > (NumberOfTicks * SecondsPerTick)) Then
			SecondsPerTick = 2
		End If
		If (NumberOfSeconds > (NumberOfTicks * SecondsPerTick)) Then
			SecondsPerTick = 5
		End If
		If (NumberOfSeconds > (NumberOfTicks * SecondsPerTick)) Then
			SecondsPerTick = 10
		End If
		If (NumberOfSeconds > (NumberOfTicks * SecondsPerTick)) Then
			SecondsPerTick = 15
		End If
		If (NumberOfSeconds > (NumberOfTicks * SecondsPerTick)) Then
			SecondsPerTick = 30
		End If
		If (NumberOfSeconds > (NumberOfTicks * SecondsPerTick)) Then
			SecondsPerTick = 60
		End If
		If (NumberOfSeconds > (NumberOfTicks * SecondsPerTick)) Then
			SecondsPerTick = 120
		End If

		SamplesPerTick = SecondsPerTick * SAMPLES_PER_SECOND

        Dim H As Integer = SamplesPerTick / 2   ' the span of the label text
        Dim X, Time, Minutes, Seconds As Integer
        Time = -SecondsPerTick
		X = 0

		Do While (X < (FirstSample + H))
            X += SamplesPerTick
            Time += SecondsPerTick
		Loop

Again:  Time += SecondsPerTick
        Minutes = Int(Time / 60)
        Seconds = Time - Minutes * 60

		If (X < (LastSample - H)) Then
			Tick_series.Points.AddXY(X, YSCALE)
			Tick_series.Points.AddXY(X, -YSCALE)
			Tick_series.Points.AddXY(X, YSCALE)
            area.AxisX.CustomLabels.Add(X - H, X + H, Minutes.ToString + ":" + Seconds.ToString("00"))
			X += SamplesPerTick
			GoTo Again
		End If

	End Sub


	Public Sub Display()

		Dim area = Chart.ChartAreas(0)

		area.AxisX.Minimum = FirstSample
		area.AxisX.Maximum = LastSample
		area.AxisX.Interval = LastSample - FirstSample
		area.AxisX.IntervalOffset = 0
		area.AxisX.LabelStyle.IsEndLabelVisible = False

		area.AxisY.Interval = 2 * YSCALE

		Chart.Series.SuspendUpdates()
		Chart.Series.Clear()
		Chart.Annotations.Clear()
		Chart.AntiAliasing = True

		area.AxisX.CustomLabels.Clear()

		' if we're displaying the time scale, we need to add the scale labels
		If (TimeScale) Then AddScaleLabels(area)

		Dim SINE_FIT_series = Chart.Series.Add("SineFit")
		SINE_FIT_series.ChartType = DataVisualization.Charting.SeriesChartType.Line

		Dim HR_series = Chart.Series.Add("HR")
		HR_series.ChartType = DataVisualization.Charting.SeriesChartType.Spline

		Dim BR_series = Chart.Series.Add("BR")
		BR_series.ChartType = DataVisualization.Charting.SeriesChartType.Line

		Dim PEAK_POINT_series = Chart.Series.Add("TICK")
		With PEAK_POINT_series
			.Color = Color.Black
			.ChartType = DataVisualization.Charting.SeriesChartType.Line
            .BorderDashStyle = DataVisualization.Charting.ChartDashStyle.Dot
			.BorderWidth = 3
		End With

		Dim CC_series = Chart.Series.Add("PACE")
		With CC_series
			.IsVisibleInLegend = False
			.ChartType = DataVisualization.Charting.SeriesChartType.Point
			.MarkerStyle = DataVisualization.Charting.MarkerStyle.None
			.MarkerSize = 0
		End With

		Dim TL_series = Chart.Series.Add("EX")
		TL_series.ChartType = DataVisualization.Charting.SeriesChartType.Spline

		Dim BE_series = Chart.Series.Add("BE") ' Breath Excursion Series
		BE_series.ChartType = DataVisualization.Charting.SeriesChartType.Spline

		If (Monochrome) Then
			HR_series.Color = Color.Black
            HR_series.BorderWidth = 3

            BR_series.Color = Color.DarkGray
			BR_series.BorderWidth = 3

            BE_series.Color = Color.DarkGray    ' breathing trendline
            BE_series.BorderWidth = 5
			BE_series.BorderDashStyle = DataVisualization.Charting.ChartDashStyle.Dash

            TL_series.Color = Color.Black       ' heartrate trendline
            TL_series.BorderWidth = 5
            TL_series.BorderDashStyle = DataVisualization.Charting.ChartDashStyle.Dash

            SINE_FIT_series.Color = Color.Silver
			SINE_FIT_series.BorderWidth = 20
		Else
			HR_series.Color = Color.Red
			HR_series.BorderWidth = 3
			BR_series.Color = Color.Blue
			BR_series.BorderWidth = 3
			BE_series.Color = Color.Orange
			BE_series.BorderWidth = 5
			TL_series.Color = Color.LawnGreen
			TL_series.BorderWidth = 5
			SINE_FIT_series.Color = Color.LightGray
			SINE_FIT_series.BorderWidth = 10
		End If


		'======================================================================
		If (BreathingToolStripMenuItem.Checked) Then
			Dim StepSize = Int((LastSample - FirstSample) / Chart.Width)
			If StepSize < 1 Then StepSize = 1
			For n = FirstSample To LastSample Step StepSize
				BR_series.Points.AddXY(n, SampleSet(n, 1))	 ' breathing
			Next
		End If

		'======================================================================
		If (HeartRateToolStripMenuItem.Checked) Then
			For n = 0 To RwaveCount - 1
				If RwaveTime(n) >= FirstSample And RwaveTime(n) <= LastSample Then
					HR_series.Points.AddXY(RwaveTime(n), RwaveVal(n))
				End If
			Next
		End If

		'======================================================================
		If (HeartRateTrendToolStripMenuItem.Checked) Then
			For i = 0 To LastPeak - 1
				If PeakTime(i) >= FirstSample And PeakTime(i) <= LastSample Then
					TL_series.Points.AddXY(PeakTime(i), RRVal(i))
				End If
			Next
		End If

		'======================================================================
		If (BreathingTrendToolStripMenuItem.Checked) Then
			For i = 0 To LastBreathPeak - 1
				If PeakBreathTimes(i) >= FirstSample And PeakBreathTimes(i) <= LastSample Then
					BE_series.Points.AddXY(PeakBreathTimes(i), BRVal(i))
				End If
			Next
		End If

		'======================================================================
		If (MaxExcursionToolStripMenuItem.Checked) Then

			PEAK_POINT_series.Points.AddXY(PeakPoint, YSCALE)
			PEAK_POINT_series.Points.AddXY(PeakPoint, -YSCALE * 0.75)

			'======================================================================
			Dim FirstSine = PeakPoint - SAMPLES_PER_SECOND * SINE_FIT_SECONDS / 2
			Dim LastSine = PeakPoint + SAMPLES_PER_SECOND * SINE_FIT_SECONDS / 2
			If FirstSine < FirstSample Then FirstSine = FirstSample
			If LastSine > LastSample Then LastSine = LastSample
			For n = FirstSine To LastSine
				SINE_FIT_series.Points.AddXY(n, SampleSet(n, 2))
			Next

			'======================================================================
			Dim Anote = New DataVisualization.Charting.TextAnnotation
			Dim Pt = CC_series.Points.AddXY(PeakPoint, -YSCALE)

			Anote.Text = String.Format("{0:F2}", ResonanceBpm)
			Anote.Font = New System.Drawing.Font("Verdana", 14)
			Anote.AnchorDataPoint = CC_series.Points(Pt)
			Chart.Annotations.Add(Anote)
		End If

		'======================================================================
		Chart.Series.ResumeUpdates()
		Chart.Refresh()

	End Sub
	Private Sub Chart_Resize(ByVal sender As Object, ByVal e As System.EventArgs) Handles Chart.Resize

		If (FileProcessed) Then Display()

	End Sub
	Private Sub Chart_MouseWheel(ByVal sender As Object, ByVal e As MouseEventArgs) Handles Me.MouseWheel

		Dim Clicks = e.Delta, Span, Center As Integer

		Span = LastSample - FirstSample + 1	' get the initial span before the zoom-in / zoom-out
		Center = Int((LastSample + FirstSample) / 2)

		If Clicks < 0 Then					' decrease the span -- zoom IN
			Span = Span * 0.9
			If Span < 100 Then Span = 100 ' clamp the zoom-in extent
		Else								' increase the span -- zoom OUT
			Span = Span / 0.9
			If Span > SampleCount Then Span = SampleCount
		End If

		UpdateDisplay(Span, Center)

	End Sub
	Private Sub HScrollBar_ValueChanged(ByVal sender As System.Object, ByVal e As EventArgs) Handles HScrollBar.ValueChanged

		Dim Span = LastSample - FirstSample

		FirstSample = HScrollBar.Value
		LastSample = FirstSample + Span
		Display()

	End Sub
	Public Sub UpdateDisplay(ByVal Span As Integer, ByVal Center As Integer)

		FirstSample = Int(Center - Span / 2)
		LastSample = Int(Center + Span / 2)

		If FirstSample < 0 Then
			LastSample = LastSample - FirstSample
			FirstSample = 0
		End If

		If LastSample > SampleCount Then
			FirstSample = FirstSample - LastSample + SampleCount
			LastSample = LastSample - LastSample + SampleCount
		End If

		If FirstSample < 0 Then FirstSample = 0
		If LastSample > SampleCount - 1 Then LastSample = SampleCount - 1

		HScrollBar.LargeChange = LastSample - FirstSample
		HScrollBar.Value = FirstSample
		HScrollBar.SmallChange = (LastSample - FirstSample + 1) / 20

		Display()

	End Sub
	Private Sub ZoomInToolStripMenuItem1_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ZoomInToolStripMenuItem1.Click

		Dim Span = LastSample - FirstSample + 1	' get the initial span before the zoom-in / zoom-out
		Dim Center = Int((LastSample + FirstSample) / 2)

		Span = Span * 0.9
		If Span < 100 Then Span = 100

		UpdateDisplay(Span, Center)

	End Sub
	Private Sub ZoomOutToolStripMenuItem2_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ZoomOutToolStripMenuItem2.Click

		Dim Span = LastSample - FirstSample + 1	' get the initial span before the zoom-in / zoom-out
		Dim Center = Int((LastSample + FirstSample) / 2)

		Span = Span / 0.9
		If Span > SampleCount Then Span = SampleCount

		UpdateDisplay(Span, Center)

	End Sub
	Private Sub CopyToolStripMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CopyToolStripMenuItem.Click
		Using ms As New IO.MemoryStream()
			Try
				Chart.SaveImage(ms, System.Drawing.Imaging.ImageFormat.Png)
				ms.Seek(0, SeekOrigin.Begin)
				Using mf As New Bitmap(ms)
					Clipboard.SetImage(mf)
				End Using
			Finally
				ms.Close()
			End Try
		End Using
	End Sub

	Private Sub ColorBWToolStripMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ColorBWToolStripMenuItem.Click
		Monochrome = Not Monochrome	' this toggles between color display and black & white
		ChartSetup()
		Display()
	End Sub

	Private Sub ToggleTimeScaleToolStripItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles TimeScaleMenuItem.Click
		TimeScale = Not TimeScale	' this toggles the scale On and Off
		ChartSetup()
		Display()
	End Sub

	'===================================================================================================================
	' the 5 items below are the five trace on/off toggles. They simply request a redraw under the then-toggled condition
	'===================================================================================================================
	Private Sub HeartRateToolStripMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles HeartRateToolStripMenuItem.Click
		Display()
	End Sub
	Private Sub BreathingToolStripMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles BreathingToolStripMenuItem.Click
		Display()
	End Sub
	Private Sub HeartRateTrendToolStripMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles HeartRateTrendToolStripMenuItem.Click
		Display()
	End Sub
	Private Sub BreathingTrendToolStripMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles BreathingTrendToolStripMenuItem.Click
		Display()
	End Sub
	Private Sub MaxExcursionToolStripMenuItem_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MaxExcursionToolStripMenuItem.Click
		Display()
	End Sub

End Class
