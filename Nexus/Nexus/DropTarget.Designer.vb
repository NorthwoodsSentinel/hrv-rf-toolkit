<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class DropTarget
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
		Me.DropInstruction = New System.Windows.Forms.Label
		Me.Chart = New System.Windows.Forms.DataVisualization.Charting.Chart
		Me.StatusStrip = New System.Windows.Forms.StatusStrip
		Me.ToolStripStatusLabel1 = New System.Windows.Forms.ToolStripStatusLabel
		Me.MenuStrip = New System.Windows.Forms.MenuStrip
		Me.PrintToolStripMenuItem = New System.Windows.Forms.ToolStripMenuItem
		Me.HScrollBar = New System.Windows.Forms.HScrollBar
		CType(Me.Chart, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.StatusStrip.SuspendLayout()
		Me.MenuStrip.SuspendLayout()
		Me.SuspendLayout()
		'
		'DropInstruction
		'
		Me.DropInstruction.BackColor = System.Drawing.SystemColors.Control
		Me.DropInstruction.Cursor = System.Windows.Forms.Cursors.Arrow
		Me.DropInstruction.Dock = System.Windows.Forms.DockStyle.Fill
		Me.DropInstruction.Font = New System.Drawing.Font("Microsoft Sans Serif", 24.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.DropInstruction.ForeColor = System.Drawing.Color.FromArgb(CType(CType(0, Byte), Integer), CType(CType(0, Byte), Integer), CType(CType(192, Byte), Integer))
		Me.DropInstruction.Location = New System.Drawing.Point(0, 0)
		Me.DropInstruction.Margin = New System.Windows.Forms.Padding(2, 0, 2, 0)
		Me.DropInstruction.Name = "DropInstruction"
		Me.DropInstruction.Size = New System.Drawing.Size(570, 394)
		Me.DropInstruction.TabIndex = 1
		Me.DropInstruction.Text = "Drop Nexus data file here" & Global.Microsoft.VisualBasic.ChrW(13) & Global.Microsoft.VisualBasic.ChrW(10) & "to process and display..."
		Me.DropInstruction.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		Me.DropInstruction.Visible = False
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
		'StatusStrip
		'
		Me.StatusStrip.Font = New System.Drawing.Font("Segoe UI", 7.8!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.StatusStrip.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.ToolStripStatusLabel1})
		Me.StatusStrip.Location = New System.Drawing.Point(0, 352)
		Me.StatusStrip.Name = "StatusStrip"
		Me.StatusStrip.Padding = New System.Windows.Forms.Padding(1, 0, 10, 0)
		Me.StatusStrip.Size = New System.Drawing.Size(570, 42)
		Me.StatusStrip.TabIndex = 3
		Me.StatusStrip.Text = "StatusStrip"
		'
		'ToolStripStatusLabel1
		'
		Me.ToolStripStatusLabel1.Font = New System.Drawing.Font("Segoe UI", 19.8!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.ToolStripStatusLabel1.Name = "ToolStripStatusLabel1"
		Me.ToolStripStatusLabel1.Size = New System.Drawing.Size(571, 37)
		Me.ToolStripStatusLabel1.Text = "Red: Heartrate / Blue: Respiration / Green: HRV"
		'
		'MenuStrip
		'
		Me.MenuStrip.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.PrintToolStripMenuItem})
		Me.MenuStrip.Location = New System.Drawing.Point(0, 0)
		Me.MenuStrip.Name = "MenuStrip"
		Me.MenuStrip.Padding = New System.Windows.Forms.Padding(4, 2, 0, 2)
		Me.MenuStrip.Size = New System.Drawing.Size(570, 24)
		Me.MenuStrip.TabIndex = 4
		Me.MenuStrip.Text = "MenuStrip"
		'
		'PrintToolStripMenuItem
		'
		Me.PrintToolStripMenuItem.Name = "PrintToolStripMenuItem"
		Me.PrintToolStripMenuItem.Size = New System.Drawing.Size(41, 20)
		Me.PrintToolStripMenuItem.Text = "Print"
		'
		'HScrollBar
		'
		Me.HScrollBar.Dock = System.Windows.Forms.DockStyle.Bottom
		Me.HScrollBar.Location = New System.Drawing.Point(0, 316)
		Me.HScrollBar.Maximum = 1000
		Me.HScrollBar.Name = "HScrollBar"
		Me.HScrollBar.Size = New System.Drawing.Size(570, 36)
		Me.HScrollBar.TabIndex = 5
		'
		'DropTarget
		'
		Me.AllowDrop = True
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.ClientSize = New System.Drawing.Size(570, 394)
		Me.Controls.Add(Me.HScrollBar)
		Me.Controls.Add(Me.StatusStrip)
		Me.Controls.Add(Me.MenuStrip)
		Me.Controls.Add(Me.Chart)
		Me.Controls.Add(Me.DropInstruction)
		Me.Cursor = System.Windows.Forms.Cursors.Arrow
		Me.MainMenuStrip = Me.MenuStrip
		Me.Margin = New System.Windows.Forms.Padding(2)
		Me.MinimumSize = New System.Drawing.Size(578, 421)
		Me.Name = "DropTarget"
		Me.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen
		Me.Text = "Heart Rate Variability Visualizer"
		CType(Me.Chart, System.ComponentModel.ISupportInitialize).EndInit()
		Me.StatusStrip.ResumeLayout(False)
		Me.StatusStrip.PerformLayout()
		Me.MenuStrip.ResumeLayout(False)
		Me.MenuStrip.PerformLayout()
		Me.ResumeLayout(False)
		Me.PerformLayout()

	End Sub
    Friend WithEvents DropInstruction As System.Windows.Forms.Label
    Friend WithEvents Chart As System.Windows.Forms.DataVisualization.Charting.Chart
    Friend WithEvents StatusStrip As System.Windows.Forms.StatusStrip
    Friend WithEvents ToolStripStatusLabel1 As System.Windows.Forms.ToolStripStatusLabel
    Friend WithEvents MenuStrip As System.Windows.Forms.MenuStrip
    Friend WithEvents PrintToolStripMenuItem As System.Windows.Forms.ToolStripMenuItem
    Friend WithEvents HScrollBar As System.Windows.Forms.HScrollBar

End Class
