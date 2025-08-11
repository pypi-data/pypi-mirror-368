# Flow SDK Feature Design: Pricing Visualization & Topology Specification

## Executive Summary

This design document outlines two key feature enhancements for the Flow SDK:
1. **Pricing Visualization**: Real-time spot price monitoring and historical pricing data access
2. **Topology Specification**: Declarative network topology and placement constraints for distributed workloads

Both features follow Flow's design principles: explicit behavior, one obvious way, 80/20 optimization, and clean abstractions without leaks.

## 1. Pricing Visualization Feature

### Current State

The SDK currently provides:
- Static limit price configuration via `DEFAULT_PRICING` in `flow/_internal/pricing.py:11`
- User overrides via `~/.flow/config.yaml`
- Basic pricing display through `flow pricing` command (`flow/cli/commands/pricing.py:18`)
- API endpoint for spot availability at `/v2/spot/availability` (`flow/providers/mithril/provider.py:3711`)

### Design Goals

1. **Real-time visibility**: Show current spot prices, not just limit prices
2. **Historical context**: Access price trends for informed bidding
3. **Multi-channel delivery**: Terminal display and web dashboard links
4. **Zero-friction access**: Information available without authentication where possible

### Implementation Architecture

#### 1.1 Core Pricing Service

Create `flow/_internal/pricing/service.py`:

```python
class PricingService:
    """Centralized pricing data aggregation and caching.
    
    Follows single responsibility principle - only handles pricing data,
    not display or formatting.
    """
    
    def get_spot_prices(
        self,
        instance_types: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> SpotPriceData:
        """Fetch current spot prices from provider API."""
        
    def get_price_history(
        self,
        instance_type: str,
        region: str,
        duration_hours: int = 24
    ) -> PriceHistory:
        """Retrieve historical pricing data."""
        
    def get_price_dashboard_url(
        self,
        instance_type: Optional[str] = None,
        region: Optional[str] = None
    ) -> str:
        """Generate dashboard URL for web-based price visualization."""
```

#### 1.2 Enhanced CLI Command

Extend `flow/cli/commands/pricing.py`:

```python
class PricingCommand(BaseCommand):
    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option("--spot", is_flag=True, help="Show current spot prices")
        @click.option("--history", type=int, help="Show price history (hours)")
        @click.option("--instance-type", "-i", help="Filter by instance type")
        @click.option("--region", "-r", help="Filter by region")
        @click.option("--web", is_flag=True, help="Open price dashboard in browser")
        @click.option("--format", type=click.Choice(["table", "json", "csv"]))
        def pricing(spot, history, instance_type, region, web, format):
            if web:
                # Open dashboard URL
                url = pricing_service.get_price_dashboard_url(instance_type, region)
                click.launch(url)
                return
                
            if spot:
                # Display real-time spot prices
                prices = pricing_service.get_spot_prices(
                    instance_types=[instance_type] if instance_type else None,
                    regions=[region] if region else None
                )
                _display_spot_prices(prices, format)
```

#### 1.3 Price Data Models

Create `flow/_internal/pricing/models.py`:

```python
class SpotPrice(BaseModel):
    """Point-in-time spot price for an instance type."""
    instance_type: str
    region: str
    current_price: float
    last_updated: datetime
    availability: int  # Available capacity
    trend: Literal["up", "down", "stable"]  # 1hr trend
    
class PriceHistory(BaseModel):
    """Historical pricing data for analysis."""
    instance_type: str
    region: str
    data_points: List[PriceDataPoint]
    statistics: PriceStatistics
    
class PriceStatistics(BaseModel):
    """Statistical analysis of price history."""
    min: float
    max: float
    avg: float
    median: float
    p95: float  # 95th percentile
    volatility: float  # Standard deviation
```

#### 1.4 Terminal Display Enhancement

Create `flow/cli/utils/price_renderer.py`:

```python
def render_spot_prices(prices: List[SpotPrice]) -> Table:
    """Render spot prices with visual indicators.
    
    Shows trend arrows, color coding for price levels,
    and availability indicators.
    """
    table = create_flow_table(title="Current Spot Prices")
    table.add_column("Instance", style="accent")
    table.add_column("Region", style="dim")
    table.add_column("Price", justify="right")
    table.add_column("Trend", justify="center")
    table.add_column("Avail", justify="right")
    
    for price in prices:
        trend_icon = _get_trend_icon(price.trend)
        price_color = _get_price_color(price.current_price, price.instance_type)
        table.add_row(
            price.instance_type,
            price.region,
            f"[{price_color}]${price.current_price:.2f}/hr[/]",
            trend_icon,
            str(price.availability)
        )
```

### API Integration Points

1. **Mithril Provider**: Extend existing `/v2/spot/availability` usage
2. **New endpoint needed**: `/v2/spot/history` for historical data
3. **Dashboard URL pattern**: `https://dashboard.mithril.ai/pricing?instance={type}&region={region}`

## 2. Topology Specification System

### Current State

The SDK currently supports:
- Basic instance count via `num_instances` field (`flow/api/models.py:622`)
- Interconnect data in auction selection (`flow/providers/mithril/bidding/finder.py:42-43`)
- No explicit topology or placement constraints

### Design Goals

1. **Declarative topology**: Express network requirements without implementation details
2. **Placement constraints**: Control co-location and anti-affinity
3. **Performance guarantees**: Specify interconnect requirements
4. **Progressive disclosure**: Simple defaults, advanced options available

### Implementation Architecture

#### 2.1 Topology Models

Create `flow/api/topology.py`:

```python
class TopologySpec(BaseModel):
    """Declarative topology specification for distributed workloads.
    
    Philosophy: Express intent, not implementation.
    The provider translates intent to actual placement.
    """
    
    # Placement strategy
    placement: Literal["packed", "spread", "cluster"] = Field(
        "packed",
        description=(
            "packed: Minimize network distance (same rack/zone)\n"
            "spread: Maximize fault tolerance (different zones)\n"
            "cluster: Balance performance and reliability"
        )
    )
    
    # Network requirements
    interconnect: Optional[InterconnectSpec] = None
    
    # Explicit constraints
    constraints: Optional[PlacementConstraints] = None
    
class InterconnectSpec(BaseModel):
    """Network interconnect requirements."""
    
    intranode: Optional[Literal["nvlink", "pcie", "any"]] = Field(
        None,
        description="GPU-to-GPU within node"
    )
    
    internode: Optional[Literal["infiniband", "roce", "ethernet", "any"]] = Field(
        None,
        description="Node-to-node network"
    )
    
    min_bandwidth_gbps: Optional[float] = Field(
        None,
        description="Minimum internode bandwidth"
    )
    
class PlacementConstraints(BaseModel):
    """Explicit placement constraints."""
    
    same_zone: bool = Field(
        False,
        description="Require all instances in same availability zone"
    )
    
    same_rack: bool = Field(
        False,
        description="Require all instances in same rack (if supported)"
    )
    
    max_distance: Optional[Literal["rack", "zone", "region"]] = Field(
        None,
        description="Maximum network distance between instances"
    )
    
    anti_affinity_groups: Optional[List[str]] = Field(
        None,
        description="Don't place with instances from these groups"
    )
```

#### 2.2 TaskConfig Extension

Extend `flow/api/models.py:536`:

```python
class TaskConfig(BaseModel):
    # ... existing fields ...
    
    # Topology specification
    topology: Optional[Union[TopologySpec, Dict[str, Any]]] = Field(
        None,
        description="Network topology and placement requirements"
    )
    
    @field_validator("topology", mode="before")
    def parse_topology(cls, v):
        """Parse topology from dict or string shorthand."""
        if isinstance(v, str):
            # Support shorthand: "packed", "spread", "cluster"
            return TopologySpec(placement=v)
        if isinstance(v, dict):
            return TopologySpec(**v)
        return v
```

#### 2.3 Provider Integration

Extend `flow/providers/mithril/provider.py`:

```python
class MithrilProvider:
    def _build_bid_request(self, config: TaskConfig) -> Dict:
        """Build bid request with topology constraints."""
        
        # Existing bid building logic
        bid = self._base_bid_request(config)
        
        # Add topology specifications
        if config.topology:
            bid["placement_spec"] = self._translate_topology(config.topology)
            
    def _translate_topology(self, topology: TopologySpec) -> Dict:
        """Translate abstract topology to provider-specific format."""
        
        spec = {}
        
        # Placement strategy
        if topology.placement == "packed":
            spec["affinity"] = "cluster"
        elif topology.placement == "spread":
            spec["anti_affinity"] = True
            
        # Interconnect requirements
        if topology.interconnect:
            if topology.interconnect.intranode:
                spec["gpu_interconnect"] = topology.interconnect.intranode
            if topology.interconnect.internode:
                spec["network_tier"] = topology.interconnect.internode
                
        # Explicit constraints
        if topology.constraints:
            if topology.constraints.same_zone:
                spec["zone_affinity"] = "required"
            if topology.constraints.same_rack:
                spec["rack_affinity"] = "required"
                
        return spec
```

#### 2.4 Auction Selection Enhancement

Extend `flow/providers/mithril/bidding/finder.py:31`:

```python
class AuctionCriteria(BaseModel):
    # ... existing fields ...
    
    # Topology requirements
    placement: Optional[str] = Field(None, description="Placement strategy")
    min_bandwidth_gbps: Optional[float] = Field(None, description="Min network bandwidth")
    
    @model_validator(mode="after")
    def validate_topology_feasibility(self):
        """Ensure topology requirements are achievable."""
        if self.num_gpus and self.num_gpus > 8 and self.intranode_interconnect == "nvlink":
            # NVLink typically limited to 8 GPUs per node
            raise ValueError("NVLink interconnect limited to 8 GPUs per node")
        return self
```

### Usage Examples

#### Example 1: Training Large Language Model
```yaml
name: llm-training
instance_type: 8xh100
num_instances: 4
topology:
  placement: packed  # Minimize communication latency
  interconnect:
    intranode: nvlink  # Fast GPU-to-GPU
    internode: infiniband  # Fast node-to-node
command: python train_llm.py
```

#### Example 2: Distributed Inference
```yaml
name: inference-cluster
instance_type: a100
num_instances: 10
topology:
  placement: spread  # Maximize availability
  constraints:
    max_distance: zone  # Different zones OK
command: python serve.py
```

#### Example 3: Data Parallel Training
```yaml
name: data-parallel
instance_type: 4xa100
num_instances: 8
topology:
  interconnect:
    min_bandwidth_gbps: 100  # Need fast data transfer
  constraints:
    same_zone: true  # Consistent latency
```

## Implementation Plan

### Phase 1: Pricing Visualization (Week 1-2)

1. **Day 1-2**: Implement `PricingService` with caching
2. **Day 3-4**: Extend CLI command with `--spot` flag
3. **Day 5-6**: Add terminal rendering with trends
4. **Day 7-8**: Implement web dashboard URL generation
5. **Day 9-10**: Testing and documentation

### Phase 2: Topology Specification (Week 3-4)

1. **Day 1-2**: Define topology models and validators
2. **Day 3-4**: Extend TaskConfig with topology field
3. **Day 5-6**: Implement provider translation layer
4. **Day 7-8**: Enhance auction selection logic
5. **Day 9-10**: Integration testing with real workloads

### Testing Strategy

1. **Unit tests**: Each new module with 90%+ coverage
2. **Integration tests**: End-to-end pricing and topology flows
3. **Performance tests**: Caching effectiveness, API latency
4. **User acceptance**: Beta testing with key users

### Migration Path

1. **Backward compatibility**: All changes additive, no breaking changes
2. **Feature flags**: New features behind flags initially
3. **Gradual rollout**: Pricing first (read-only), then topology (affects allocation)

## Design Decisions & Rationale

### Why separate pricing service?
- **Single Responsibility**: Pricing logic isolated from display
- **Testability**: Mock service for testing
- **Extensibility**: Easy to add new data sources

### Why abstract topology model?
- **Provider agnostic**: Not tied to Mithril specifics
- **Future proof**: Can add Kubernetes, Slurm backends
- **User friendly**: Express intent, not implementation

### Why not automatic topology inference?
- **Explicit is better**: Users should declare requirements
- **Predictability**: No surprising placement decisions
- **Cost control**: Topology affects pricing

## Security & Privacy Considerations

1. **Pricing data**: Public information, no auth required
2. **Topology specs**: Part of task config, user-scoped
3. **Dashboard URLs**: No sensitive data in query params
4. **Caching**: Respect user privacy, cache per-user

## Performance Considerations

1. **API calls**: Cache aggressively (15min for prices)
2. **Terminal rendering**: Stream output for large tables
3. **Web dashboard**: Generate URL client-side
4. **Topology validation**: Fail fast at config time

## Open Questions

1. **Historical data retention**: How far back for price history?
2. **Dashboard hosting**: Self-hosted or use provider's dashboard?
3. **Topology conflicts**: How to handle unsatisfiable constraints?
4. **Pricing alerts**: Should we add price threshold notifications?

## Conclusion

These features address core user needs while maintaining Flow's design principles. The pricing visualization provides transparency for cost optimization, while topology specification enables performance optimization for distributed workloads. Both features integrate cleanly with existing architecture and provide clear upgrade paths.