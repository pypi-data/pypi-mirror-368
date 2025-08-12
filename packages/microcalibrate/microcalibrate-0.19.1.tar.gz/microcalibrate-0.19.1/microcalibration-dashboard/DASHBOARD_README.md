# Calibration dashboard

A dashboard for visualizing microcalibrate training logs. This Next.js application provides interactive charts and metrics to help debug calibration progress.

## Getting started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
make dashboard-install
```

### Development

```bash
make dashboard-dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

### Usage

1. **Load data**: 
   - Use the file upload area to select a CSV file containing calibration logs
   - Or drag and drop the CSV file onto the upload area

2. **View metrics**: 
   - Overview cards show key statistics about the calibration run
   - Total epochs, number of targets, final loss, and convergence point

3. **Analyze loss**: 
   - The loss chart shows training progress over epochs
   - Uses logarithmic scale for better visualization of small values

4. **Examine errors**: 
   - Two charts show absolute and relative errors for each target
   - Filter specific targets using the target selector

5. **Filter targets**: 
   - Use checkboxes to show/hide specific calibration targets
   - Useful when dealing with many targets

## CSV Format

The dashboard expects CSV files with the following columns:
- `epoch`: Training epoch number
- `loss`: Loss value at that epoch
- `target_name`: Name of the calibration target
- `target`: Target value
- `estimate`: Estimated value
- `error`: Difference between estimate and target
- `abs_error`: Absolute error
- `rel_abs_error`: Relative absolute error

Example:
```csv
,epoch,loss,target_name,target,estimate,error,abs_error,rel_abs_error
0,0,0.011227985844016075,income_aged_20_30,245346.078125,218048.453125,-27297.625,27297.625,0.11126171328523249
1,0,0.011227985844016075,income_aged_40_50,1237963.125,1113685.0,-124278.125,124278.125,0.10038919778002273
```

## Sample data

A sample CSV file is included in the `public/` directory for testing purposes.

## Building for production

```bash
make dashboard-build
make dahsboard-start
```

## Technology stack

- **Next.js 15**: React framework with App Router
- **TypeScript**: Type safety and better development experience
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Interactive charts built on D3
- **Papa Parse**: CSV parsing library
- **Lucide React**: Modern icon library

## Contributing

When adding new features or fixing issues:

1. Follow the existing code structure and TypeScript patterns
2. Add appropriate type definitions in `src/types/`
3. Create reusable components in `src/components/`
4. Use Tailwind CSS for styling consistency
5. Test with various CSV formats and data sizes
