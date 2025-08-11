use crate::enrichment::SwapEnricher;
use crate::schema::SwapEvent;
use crate::service::DextradesService;
use async_trait::async_trait;
use eyre::Result;
use serde_json;

/// Enricher that determines trade direction and calculates decimal amounts
pub struct TradeDirectionEnricher;

#[async_trait]
impl SwapEnricher for TradeDirectionEnricher {
    fn name(&self) -> &'static str {
        "trade_direction"
    }

    fn required_fields(&self) -> Vec<&'static str> {
        vec![
            "token0_address",
            "token1_address",
            "token0_symbol",
            "token1_symbol",
            "token0_decimals",
            "token1_decimals",
        ]
    }

    fn provided_fields(&self) -> Vec<&'static str> {
        vec![
            "token_bought_address",
            "token_sold_address",
            "token_bought_symbol",
            "token_sold_symbol",
            "token_bought_amount_raw",
            "token_sold_amount_raw",
            "token_bought_amount",
            "token_sold_amount",
            "trade_direction",
        ]
    }

    async fn enrich(&self, events: &mut [SwapEvent], _service: &DextradesService) -> Result<()> {
        for event in events {
            // Apply protocol-specific trade direction logic
            match event.dex_protocol.as_str() {
                "uniswap_v2" => {
                    self.enrich_v2_trade_direction(event)?;
                }
                "uniswap_v3" => {
                    self.enrich_v3_trade_direction(event)?;
                }
                _ => {
                    log::warn!(
                        "Unknown protocol for trade direction: {}",
                        event.dex_protocol
                    );
                }
            }
        }

        Ok(())
    }
}

impl TradeDirectionEnricher {
    /// Enrich V2 trade direction by delegating to the protocol module
    fn enrich_v2_trade_direction(&self, event: &mut SwapEvent) -> Result<()> {
        // Create a temporary vector to reuse shared protocol logic
        let mut temp_events = vec![event.clone()];

        // Protocol-specific direction resolution (with internal fallback logic)
        crate::protocols::uniswap_v2::enrich_trade_direction(&mut temp_events);
        // Decimal amounts depend on direction; compute after direction is set
        crate::protocols::uniswap_v2::calculate_decimal_amounts(&mut temp_events);

        // Copy results back to the original event
        if let Some(enriched_event) = temp_events.into_iter().next() {
            // Copy trade direction fields
            if let Some(addr) = &enriched_event.token_bought_address {
                event.add_enriched_field(
                    "token_bought_address".to_string(),
                    serde_json::Value::String(addr.clone()),
                );
                event.token_bought_address = Some(addr.clone());
            }

            if let Some(addr) = &enriched_event.token_sold_address {
                event.add_enriched_field(
                    "token_sold_address".to_string(),
                    serde_json::Value::String(addr.clone()),
                );
                event.token_sold_address = Some(addr.clone());
            }

            if let Some(symbol) = &enriched_event.token_bought_symbol {
                event.add_enriched_field(
                    "token_bought_symbol".to_string(),
                    serde_json::Value::String(symbol.clone()),
                );
                event.token_bought_symbol = Some(symbol.clone());
            }

            if let Some(symbol) = &enriched_event.token_sold_symbol {
                event.add_enriched_field(
                    "token_sold_symbol".to_string(),
                    serde_json::Value::String(symbol.clone()),
                );
                event.token_sold_symbol = Some(symbol.clone());
            }

            if let Some(amount_raw) = &enriched_event.token_bought_amount_raw {
                event.add_enriched_field(
                    "token_bought_amount_raw".to_string(),
                    serde_json::Value::String(amount_raw.clone()),
                );
                event.token_bought_amount_raw = Some(amount_raw.clone());
            }

            if let Some(amount_raw) = &enriched_event.token_sold_amount_raw {
                event.add_enriched_field(
                    "token_sold_amount_raw".to_string(),
                    serde_json::Value::String(amount_raw.clone()),
                );
                event.token_sold_amount_raw = Some(amount_raw.clone());
            }

            if let Some(amount) = enriched_event.token_bought_amount {
                event.add_enriched_field(
                    "token_bought_amount".to_string(),
                    serde_json::Value::Number(
                        serde_json::Number::from_f64(amount).unwrap_or(serde_json::Number::from(0)),
                    ),
                );
                event.token_bought_amount = Some(amount);
            }

            if let Some(amount) = enriched_event.token_sold_amount {
                event.add_enriched_field(
                    "token_sold_amount".to_string(),
                    serde_json::Value::Number(
                        serde_json::Number::from_f64(amount).unwrap_or(serde_json::Number::from(0)),
                    ),
                );
                event.token_sold_amount = Some(amount);
            }

            if let Some(dir) = &enriched_event.trade_direction {
                event.add_enriched_field(
                    "trade_direction".to_string(),
                    serde_json::Value::String(dir.clone()),
                );
                event.trade_direction = Some(dir.clone());
            }
        }

        Ok(())
    }

    /// Enrich V3 trade direction using the protocol module (consumes enriched fields)
    fn enrich_v3_trade_direction(&self, event: &mut SwapEvent) -> Result<()> {
        // Create a temporary vector with just this event for the V3 enricher
        let mut temp_events = vec![event.clone()];

        // Apply V3 enrichment logic (now uses event-enriched fields directly)
        crate::protocols::uniswap_v3::enrich_trade_direction(&mut temp_events);
        crate::protocols::uniswap_v3::calculate_decimal_amounts(&mut temp_events);

        // Copy results back to the original event (same logic as V2)
        if let Some(enriched_event) = temp_events.into_iter().next() {
            // Copy trade direction fields (same as V2 logic above)
            if let Some(addr) = &enriched_event.token_bought_address {
                event.add_enriched_field(
                    "token_bought_address".to_string(),
                    serde_json::Value::String(addr.clone()),
                );
                event.token_bought_address = Some(addr.clone());
            }

            if let Some(addr) = &enriched_event.token_sold_address {
                event.add_enriched_field(
                    "token_sold_address".to_string(),
                    serde_json::Value::String(addr.clone()),
                );
                event.token_sold_address = Some(addr.clone());
            }

            if let Some(symbol) = &enriched_event.token_bought_symbol {
                event.add_enriched_field(
                    "token_bought_symbol".to_string(),
                    serde_json::Value::String(symbol.clone()),
                );
                event.token_bought_symbol = Some(symbol.clone());
            }

            if let Some(symbol) = &enriched_event.token_sold_symbol {
                event.add_enriched_field(
                    "token_sold_symbol".to_string(),
                    serde_json::Value::String(symbol.clone()),
                );
                event.token_sold_symbol = Some(symbol.clone());
            }

            if let Some(amount_raw) = &enriched_event.token_bought_amount_raw {
                event.add_enriched_field(
                    "token_bought_amount_raw".to_string(),
                    serde_json::Value::String(amount_raw.clone()),
                );
                event.token_bought_amount_raw = Some(amount_raw.clone());
            }

            if let Some(amount_raw) = &enriched_event.token_sold_amount_raw {
                event.add_enriched_field(
                    "token_sold_amount_raw".to_string(),
                    serde_json::Value::String(amount_raw.clone()),
                );
                event.token_sold_amount_raw = Some(amount_raw.clone());
            }

            if let Some(amount) = enriched_event.token_bought_amount {
                event.add_enriched_field(
                    "token_bought_amount".to_string(),
                    serde_json::Value::Number(
                        serde_json::Number::from_f64(amount).unwrap_or(serde_json::Number::from(0)),
                    ),
                );
                event.token_bought_amount = Some(amount);
            }

            if let Some(amount) = enriched_event.token_sold_amount {
                event.add_enriched_field(
                    "token_sold_amount".to_string(),
                    serde_json::Value::Number(
                        serde_json::Number::from_f64(amount).unwrap_or(serde_json::Number::from(0)),
                    ),
                );
                event.token_sold_amount = Some(amount);
            }

            if let Some(dir) = &enriched_event.trade_direction {
                event.add_enriched_field(
                    "trade_direction".to_string(),
                    serde_json::Value::String(dir.clone()),
                );
                event.trade_direction = Some(dir.clone());
            }
        }

        Ok(())
    }
}
