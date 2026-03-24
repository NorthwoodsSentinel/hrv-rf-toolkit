<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class HRV_Display
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
		Dim ChartArea1 As System.Windows.Forms.DataVisualization.Charting.ChartArea = New System.Windows.Forms.DataVisualization.Charting.ChartArea
		Dim Legend1 As System.Windows.Forms.DataVisualization.Charting.Legend = New System.Windows.Forms.DataVisualization.Charting.Legend
		Dim Series1 As System.Windows.Forms.DataVisualization.Charting.Series = New System.Windows.Forms.DataVisualization.Charting.Series
		Dim Series2 As System.Windows.Forms.DataVisualization.Charting.Series = New System.Windows.Forms.DataVisualization.Charting.Series
		Me.Chart = New System.Windows.Forms.DataVisualization.Charting.Chart
		Me.MenuStrip = New System.Windows.Forms.MenuStrip
		Me.CopyToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.ColorBWToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.PrintToolStripMenuItems = New System.Windows.Forms.ToolStripMenuItem
		Me.AutoZoomToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.EntireSessionToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.ZoomInToolStripMenuItem1 = New System.Windows.Forms.ToolStripMenuItem
		Me.ZoomOutToolStripMenuItem2 = New System.Windows.Forms.ToolStripMenuItem
		Me.TimeScaleMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.TracesToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.HeartRateToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.BreathingToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.HeartRateTrendToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.BreathingTrendToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.MaxExcursionToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.HScrollBar = New System.Windows.Forms.HScrollBar
		CType(Me.Chart, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.MenuStrip.SuspendLayout()
		Me.SuspendLayout()
		'
		'Chart
		'
		Me.Chart.AntiAliasing = System.Windows.Forms.DataVisualization.Charting.AntiAliasingStyles.None
		ChartArea1.AxisY.IsMarginVisible = False
		ChartArea1.AxisY2.IsMarginVisible = False
		ChartArea1.CursorX.IsUserEnabled = True
		ChartArea1.CursorX.IsUserSelectionEnabled = True
		ChartArea1.Name = "ChartArea"
		Me.Chart.ChartAreas.Add(ChartArea1)
		Me.Chart.Enabled = False
		Legend1.Enabled = False
		Legend1.Name = "Legend1"
		Me.Chart.Legends.Add(Legend1)
		Me.Chart.Location = New System.Drawing.Point(0, 0)
		Me.Chart.Margin = New System.Windows.Forms.Padding(0)
		Me.Chart.Name = "Chart"
		Series1.ChartArea = "ChartArea"
		Series1.IsVisibleInLegend = False
		Series1.Legend = "Legend1"
		Series1.Name = "Series1"
		Series2.ChartArea = "ChartArea"
		Series2.Legend = "Legend1"
		Series2.Name = "Series2"
		Me.Chart.Series.Add(Series1)
		Me.Chart.Series.Add(Series2)
		Me.Chart.Size = New System.Drawing.Size(149, 119)
		Me.Chart.TabIndex = 2
		Me.Chart.TabStop = False
		Me.Chart.Text = "Chart"
		'
		'MenuStrip
		'
		Me.MenuStrip.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.CopyToolStripMenuItem, Me.ColorBWToolStripMenuItem, Me.PrintToolStripMenuItems, Me.AutoZoomToolStripMenuItem, Me.EntireSessionToolStripMenuItem, Me.ZoomInToolStripMenuItem1, Me.ZoomOutToolStripMenuItem2, Me.TimeScaleMenuItem, Me.TracesToolStripMenuItem})
		Me.MenuStrip.Location = New System.Drawing.Point(0, 0)
		Me.MenuStrip.Name = "MenuStrip"
		Me.MenuStrip.Padding = New System.Windows.Forms.Padding(4, 2, 0, 2)
		Me.MenuStrip.Size = New System.Drawing.Size(570, 25)
		Me.MenuStrip.TabIndex = 4
		Me.MenuStrip.Text = "MenuStrip"
		'
		'CopyToolStripMenuItem
		'
		Me.CopyToolStripMenuItem.Name = "CopyToolStripMenuItem"
		Me.CopyToolStripMenuItem.Size = New System.Drawing.Size(53, 21)
		Me.CopyToolStripMenuItem.Text = "Copy"
		'
		'ColorBWToolStripMenuItem
		'
		Me.ColorBWToolStripMenuItem.Name = "ColorBWToolStripMenuItem"
		Me.ColorBWToolStripMenuItem.Size = New System.Drawing.Size(79, 21)
		Me.ColorBWToolStripMenuItem.Text = "Color/BW"
		'
		'PrintToolStripMenuItems
		'
		Me.PrintToolStripMenuItems.Name = "PrintToolStripMenuItems"
		Me.PrintToolStripMenuItems.Size = New System.Drawing.Size(48, 21)
		Me.PrintToolStripMenuItems.Text = "Print"
		'
		'AutoZoomToolStripMenuItem
		'
		Me.AutoZoomToolStripMenuItem.Name = "AutoZoomToolStripMenuItem"
		Me.AutoZoomToolStripMenuItem.Size = New System.Drawing.Size(90, 21)
		Me.AutoZoomToolStripMenuItem.Text = "Auto-Zoom"
		'
		'EntireSessionToolStripMenuItem
		'
		Me.EntireSessionToolStripMenuItem.Name = "EntireSessionToolStripMenuItem"
		Me.EntireSessionToolStripMenuItem.Size = New System.Drawing.Size(105, 21)
		Me.EntireSessionToolStripMenuItem.Text = "Entire-Session"
		'
		'ZoomInToolStripMenuItem1
		'
		Me.ZoomInToolStripMenuItem1.Name = "ZoomInToolStripMenuItem1"
		Me.ZoomInToolStripMenuItem1.Size = New System.Drawing.Size(73, 21)
		Me.ZoomInToolStripMenuItem1.Text = "Zoom-In"
		'
		'ZoomOutToolStripMenuItem2
		'
		Me.ZoomOutToolStripMenuItem2.Name = "ZoomOutToolStripMenuItem2"
		Me.ZoomOutToolStripMenuItem2.Size = New System.Drawing.Size(84, 21)
		Me.ZoomOutToolStripMenuItem2.Text = "Zoom-Out"
		'
		'TimeScaleMenuItem
		'
		Me.TimeScaleMenuItem.Name = "TimeScaleMenuItem"
		Me.TimeScaleMenuItem.Size = New System.Drawing.Size(84, 21)
		Me.TimeScaleMenuItem.Text = "Time Scale"
		'
		'TracesToolStripMenuItem
		'
		Me.TracesToolStripMenuItem.DropDownItems.AddRange(New System.Windows.Forms.ToolStripItem() {Me.HeartRateToolStripMenuItem, Me.BreathingToolStripMenuItem, Me.HeartRateTrendToolStripMenuItem, Me.BreathingTrendToolStripMenuItem, Me.MaxExcursionToolStripMenuItem})
		Me.TracesToolStripMenuItem.Name = "TracesToolStripMenuItem"
		Me.TracesToolStripMenuItem.Size = New System.Drawing.Size(60, 21)
		Me.TracesToolStripMenuItem.Text = "Traces"
		'
		'HeartRateToolStripMenuItem
		'
		Me.HeartRateToolStripMenuItem.Checked = True
		Me.HeartRateToolStripMenuItem.CheckOnClick = True
		Me.HeartRateToolStripMenuItem.CheckState = System.Windows.Forms.CheckState.Checked
		Me.HeartRateToolStripMenuItem.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Text
		Me.HeartRateToolStripMenuItem.Name = "HeartRateToolStripMenuItem"
		Me.HeartRateToolStripMenuItem.Size = New System.Drawing.Size(181, 22)
		Me.HeartRateToolStripMenuItem.Text = "Heart Rate"
		'
		'BreathingToolStripMenuItem
		'
		Me.BreathingToolStripMenuItem.Checked = True
		Me.BreathingToolStripMenuItem.CheckOnClick = True
		Me.BreathingToolStripMenuItem.CheckState = System.Windows.Forms.CheckState.Checked
		Me.BreathingToolStripMenuItem.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Text
		Me.BreathingToolStripMenuItem.Name = "BreathingToolStripMenuItem"
		Me.BreathingToolStripMenuItem.Size = New System.Drawing.Size(181, 22)
		Me.BreathingToolStripMenuItem.Text = "Breathing"
		'
		'HeartRateTrendToolStripMenuItem
		'
		Me.HeartRateTrendToolStripMenuItem.Checked = True
		Me.HeartRateTrendToolStripMenuItem.CheckOnClick = True
		Me.HeartRateTrendToolStripMenuItem.CheckState = System.Windows.Forms.CheckState.Checked
		Me.HeartRateTrendToolStripMenuItem.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Text
		Me.HeartRateTrendToolStripMenuItem.Name = "HeartRateTrendToolStripMenuItem"
		Me.HeartRateTrendToolStripMenuItem.Size = New System.Drawing.Size(181, 22)
		Me.HeartRateTrendToolStripMenuItem.Text = "Heart Rate Trend"
		'
		'BreathingTrendToolStripMenuItem
		'
		Me.BreathingTrendToolStripMenuItem.Checked = True
		Me.BreathingTrendToolStripMenuItem.CheckOnClick = True
		Me.BreathingTrendToolStripMenuItem.CheckState = System.Windows.Forms.CheckState.Checked
		Me.BreathingTrendToolStripMenuItem.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Text
		Me.BreathingTrendToolStripMenuItem.Name = "BreathingTrendToolStripMenuItem"
		Me.BreathingTrendToolStripMenuItem.Size = New System.Drawing.Size(181, 22)
		Me.BreathingTrendToolStripMenuItem.Text = "Breathing Trend"
		'
		'MaxExcursionToolStripMenuItem
		'
		Me.MaxExcursionToolStripMenuItem.Checked = True
		Me.MaxExcursionToolStripMenuItem.CheckOnClick = True
		Me.MaxExcursionToolStripMenuItem.CheckState = System.Windows.Forms.CheckState.Checked
		Me.MaxExcursionToolStripMenuItem.Name = "MaxExcursionToolStripMenuItem"
		Me.MaxExcursionToolStripMenuItem.Size = New System.Drawing.Size(181, 22)
		Me.MaxExcursionToolStripMenuItem.Text = "Max Excursion"
		'
		'HScrollBar
		'
		Me.HScrollBar.Dock = System.Windows.Forms.DockStyle.Bottom
		Me.HScrollBar.Location = New System.Drawing.Point(0, 358)
		Me.HScrollBar.Maximum = 1000
		Me.HScrollBar.Name = "HScrollBar"
		Me.HScrollBar.Size = New System.Drawing.Size(570, 36)
		Me.HScrollBar.TabIndex = 5
		'
		'HRV_Display
		'
		Me.AllowDrop = True
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.ClientSize = New System.Drawing.Size(570, 394)
		Me.Controls.Add(Me.HScrollBar)
		Me.Controls.Add(Me.MenuStrip)
		Me.Controls.Add(Me.Chart)
		Me.Cursor = System.Windows.Forms.Cursors.Arrow
		Me.MainMenuStrip = Me.MenuStrip
		Me.Margin = New System.Windows.Forms.Padding(2)
		Me.MinimumSize = New System.Drawing.Size(578, 421)
		Me.Name = "HRV_Display"
		Me.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen
		Me.Text = "Heart Rate Variability Visualizer"
		CType(Me.Chart, System.ComponentModel.ISupportInitialize).EndInit()
		Me.MenuStrip.ResumeLayout(False)
		Me.MenuStrip.PerformLayout()
		Me.ResumeLayout(False)
		Me.PerformLayout()

	End Sub
	Friend WithEvents Chart As System.Windows.Forms.DataVisualization.Charting.Chart
	Friend WithEvents MenuStrip As System.Windows.Forms.MenuStrip
	Friend WithEvents PrintToolStripMenuItems As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents HScrollBar As System.Windows.Forms.HScrollBar
	Friend WithEvents AutoZoomToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents EntireSessionToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents ZoomInToolStripMenuItem1 As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents ZoomOutToolStripMenuItem2 As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents CopyToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents ColorBWToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents TracesToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents HeartRateToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents BreathingToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents HeartRateTrendToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents BreathingTrendToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents MaxExcursionToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
	Friend WithEvents TimeScaleMenuItem As System.Windows.Forms.ToolStripMenuItem

End Class
