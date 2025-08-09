```mermaid
    classDiagram
        class Waveform{
            +samples
            +sample_rate
            +start_time
            +header
        }

        class spectral{
            +FundamentalFrequencyCalculator
            +Spectrum
            +FrameBuilder
            +TimeHistory
        }

        class timbre_features{
            +TimbreFeatures
            +EquivalentLevel
            +HarmonicMetrics
            +LevelMetrics
            +SoundQualityMetrics
            +TemporalLevelMetrics
            +TemporalMetrics
        }